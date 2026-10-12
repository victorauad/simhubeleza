using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Reflection.Emit;
using System.Text;

// Usage: Scan.exe <simhubDir> <outDir>
// Writes: calls.tsv (method, callee, recent strings), types.txt (public type members of selected types),
//         plugins.txt (plugin classes + attributes), strings-by-method for selected callee names.
class Scan
{
    static Dictionary<short, OpCode> ops = new Dictionary<short, OpCode>();
    static string dir;

    static void Main(string[] a)
    {
        dir = a[0];
        string outDir = a[1];
        Directory.CreateDirectory(outDir);
        foreach (var f in typeof(OpCodes).GetFields(BindingFlags.Public | BindingFlags.Static))
        {
            var o = (OpCode)f.GetValue(null);
            ops[o.Value] = o;
        }
        AppDomain.CurrentDomain.AssemblyResolve += (s, e) =>
        {
            var n = new AssemblyName(e.Name).Name;
            foreach (var ext in new[] { ".dll", ".exe" })
            {
                var p = Path.Combine(dir, n + ext);
                if (File.Exists(p)) try { return Assembly.LoadFrom(p); } catch { }
            }
            return null;
        };

        var files = Directory.GetFiles(dir, "*.dll").Concat(Directory.GetFiles(dir, "*.exe"))
            .Concat(Directory.Exists(Path.Combine(dir, "PluginsData")) ? new string[0] : new string[0])
            .Where(p => !Path.GetFileName(p).StartsWith("System.") && !Path.GetFileName(p).StartsWith("Microsoft.")
                     && !Path.GetFileName(p).StartsWith("CefSharp") && !Path.GetFileName(p).StartsWith("MahApps")
                     && !Path.GetFileName(p).StartsWith("NAudio") && !Path.GetFileName(p).StartsWith("SharpDX"))
            .ToList();

        var calls = new StreamWriter(Path.Combine(outDir, "calls.tsv"), false, new UTF8Encoding(false));
        var plugins = new StreamWriter(Path.Combine(outDir, "plugins.txt"), false, new UTF8Encoding(false));
        var allstr = new StreamWriter(Path.Combine(outDir, "strings.tsv"), false, new UTF8Encoding(false));
        var asmlog = new StreamWriter(Path.Combine(outDir, "assemblies.txt"), false, new UTF8Encoding(false));

        foreach (var f in files)
        {
            Assembly asm;
            try { AssemblyName.GetAssemblyName(f); asm = Assembly.UnsafeLoadFrom(f); }
            catch (Exception ex) { asmlog.WriteLine("SKIP\t" + Path.GetFileName(f) + "\t" + ex.GetType().Name); continue; }
            Type[] types;
            try { types = asm.GetTypes(); }
            catch (ReflectionTypeLoadException ex) { types = ex.Types.Where(t => t != null).ToArray(); asmlog.WriteLine("PARTIAL\t" + Path.GetFileName(f) + "\t" + (ex.LoaderExceptions.Length>0 ? ex.LoaderExceptions[0].Message : "")); }
            asmlog.WriteLine("OK\t" + Path.GetFileName(f) + "\t" + types.Length);
            asmlog.Flush();

            foreach (var t in types)
            {
                // plugin detection
                try
                {
                    var ifs = t.GetInterfaces().Select(i => i.Name).ToList();
                    if (ifs.Contains("IPlugin") && !t.IsAbstract && !t.IsInterface)
                    {
                        var attrs = new List<string>();
                        foreach (var ca in t.GetCustomAttributesData())
                        {
                            var args = string.Join(", ", ca.ConstructorArguments.Select(x => x.Value == null ? "null" : x.Value.ToString()));
                            attrs.Add(ca.AttributeType.Name + "(" + args + ")");
                        }
                        var bt = t.BaseType; var chain = new List<string>();
                        while (bt != null && bt != typeof(object)) { chain.Add(bt.ToString()); bt = bt.BaseType; }
                        plugins.WriteLine(Path.GetFileName(f) + "\t" + t.FullName + "\t" + string.Join(" ; ", attrs) + "\t" + string.Join(" <- ", chain) + "\t" + string.Join(",", ifs));
                    }
                }
                catch { }

                foreach (var m in SafeMethods(t))
                {
                    byte[] il;
                    try { var b = m.GetMethodBody(); if (b == null) continue; il = b.GetILAsByteArray(); } catch { continue; }
                    if (il == null) continue;
                    var recent = new List<string>();
                    string mname = t.FullName + "::" + m.Name;
                    int i = 0;
                    try
                    {
                        while (i < il.Length)
                        {
                            OpCode op;
                            short v = il[i];
                            if (v == 0xFE) { v = (short)(0xFE00 | il[i + 1]); i += 2; } else i += 1;
                            if (!ops.TryGetValue(v, out op)) break;
                            int operand = 0;
                            switch (op.OperandType)
                            {
                                case OperandType.InlineNone: break;
                                case OperandType.ShortInlineBrTarget: case OperandType.ShortInlineI: case OperandType.ShortInlineVar: i += 1; break;
                                case OperandType.InlineVar: i += 2; break;
                                case OperandType.InlineI8: case OperandType.InlineR: i += 8; break;
                                case OperandType.InlineSwitch: int n = BitConverter.ToInt32(il, i); i += 4 + 4 * n; break;
                                default: operand = BitConverter.ToInt32(il, i); i += 4; break;
                            }
                            if (op == OpCodes.Ldstr)
                            {
                                string s = null;
                                try { s = m.Module.ResolveString(operand); } catch { }
                                if (s != null)
                                {
                                    recent.Add("\"" + s + "\"");
                                    if (recent.Count > 30) recent.RemoveAt(0);
                                    allstr.WriteLine(Path.GetFileName(f) + "\t" + mname + "\t" + Esc(s));
                                }
                            }
                            else if (op == OpCodes.Call || op == OpCodes.Callvirt || op == OpCodes.Newobj)
                            {
                                MethodBase callee = null;
                                try { callee = m.Module.ResolveMethod(operand, SafeGen(t), m.IsGenericMethod ? m.GetGenericArguments() : null); } catch { }
                                if (callee != null)
                                {
                                    var cn = callee.Name;
                                    if (callee.DeclaringType == typeof(string) && (cn == "Concat" || cn == "Format")) recent.Add("<" + cn + ">");
                                    if (cn == "AttachDelegate" || cn == "AddProperty" || cn == "SetPropertyValue" || cn == "AddAction" || cn == "AddEvent"
                                        || cn == "TriggerEvent" || cn == "AddInputMapping" || cn == "SetProperty" || cn == "AttachProperty" || cn.StartsWith("AttachDelegate")
                                        || cn == "AddExportedProperty" || cn == "RegisterFunction" || cn == "SetValue" || cn == "AddPropertyAlias" || cn == "AddPropertyWithType")
                                    {
                                        var ctype = callee.DeclaringType == null ? "" : callee.DeclaringType.Name;
                                        string sig = "";
                                        try { sig = string.Join(",", callee.GetParameters().Select(p => p.ParameterType.Name)); } catch { }
                                        string rt = "";
                                        try { if (callee is MethodInfo) { var mi = (MethodInfo)callee; if (mi.IsGenericMethod) rt = string.Join(",", mi.GetGenericArguments().Select(g => g.IsGenericType ? g.Name.Split('`')[0] + "[" + string.Join(",", g.GetGenericArguments().Select(x => x.Name)) + "]" : g.Name)); } } catch { }
                                        calls.WriteLine(Path.GetFileName(f) + "\t" + mname + "\t" + ctype + "." + cn + "<" + rt + ">(" + sig + ")\t" + string.Join(" ", recent.Select(Esc)));
                                        if (cn != "SetValue") recent.Clear();
                                    }
                                }
                            }
                        }
                    }
                    catch { }
                }
            }
            calls.Flush(); plugins.Flush(); allstr.Flush();
        }
        calls.Close(); plugins.Close(); allstr.Close(); asmlog.Close();
    }

    static Type[] SafeGen(Type t) { try { return t.IsGenericType ? t.GetGenericArguments() : null; } catch { return null; } }
    static string Esc(string s) { return s.Replace("\\", "\\\\").Replace("\t", "\\t").Replace("\r", "\\r").Replace("\n", "\\n"); }
    static IEnumerable<MethodBase> SafeMethods(Type t)
    {
        var fl = BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Instance | BindingFlags.Static | BindingFlags.DeclaredOnly;
        MethodBase[] ms = new MethodBase[0], cs = new MethodBase[0];
        try { ms = t.GetMethods(fl); } catch { }
        try { cs = t.GetConstructors(fl); } catch { }
        return ms.Concat(cs);
    }
}

