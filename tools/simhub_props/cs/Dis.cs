using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Reflection.Emit;
using System.Text.RegularExpressions;

// Usage: Dis.exe <simhubDir> <assemblyFile> <typeRegex> <methodRegex>
class Dis
{
    static Dictionary<short, OpCode> ops = new Dictionary<short, OpCode>();
    static void Main(string[] a)
    {
        var dir = a[0];
        foreach (var f in typeof(OpCodes).GetFields(BindingFlags.Public | BindingFlags.Static)) { var o = (OpCode)f.GetValue(null); ops[o.Value] = o; }
        AppDomain.CurrentDomain.AssemblyResolve += (s, e) =>
        {
            var n = new AssemblyName(e.Name).Name;
            foreach (var ext in new[] { ".dll", ".exe" }) { var p = Path.Combine(dir, n + ext); if (File.Exists(p)) try { return Assembly.UnsafeLoadFrom(p); } catch { } }
            return null;
        };
        var asm = Assembly.UnsafeLoadFrom(Path.Combine(dir, a[1]));
        Type[] ts; try { ts = asm.GetTypes(); } catch (ReflectionTypeLoadException ex) { ts = ex.Types.Where(t => t != null).ToArray(); }
        var trx = new Regex(a[2]); var mrx = new Regex(a[3]);
        var fl = BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Instance | BindingFlags.Static | BindingFlags.DeclaredOnly;
        foreach (var t in ts.Where(t => t.FullName != null && trx.IsMatch(t.FullName)))
        {
            IEnumerable<MethodBase> ms = t.GetMethods(fl).Cast<MethodBase>().Concat(t.GetConstructors(fl));
            foreach (var m in ms.Where(m => mrx.IsMatch(m.Name)))
            {
                Console.WriteLine("=== " + t.FullName + "::" + m.Name + "(" + string.Join(", ", m.GetParameters().Select(p => p.ParameterType.Name + " " + p.Name)) + ")");
                var body = m.GetMethodBody(); if (body == null) continue;
                var il = body.GetILAsByteArray();
                int i = 0;
                var gt = t.IsGenericType ? t.GetGenericArguments() : null;
                var gm = m.IsGenericMethod ? m.GetGenericArguments() : null;
                while (i < il.Length)
                {
                    int start = i;
                    short v = il[i];
                    if (v == 0xFE) { v = (short)(0xFE00 | il[i + 1]); i += 2; } else i += 1;
                    OpCode op; if (!ops.TryGetValue(v, out op)) { Console.WriteLine("??"); break; }
                    string arg = "";
                    switch (op.OperandType)
                    {
                        case OperandType.InlineNone: break;
                        case OperandType.ShortInlineBrTarget: arg = "IL_" + (i + 1 + (sbyte)il[i]).ToString("X4"); i += 1; break;
                        case OperandType.ShortInlineI: arg = ((sbyte)il[i]).ToString(); i += 1; break;
                        case OperandType.ShortInlineVar: arg = il[i].ToString(); i += 1; break;
                        case OperandType.InlineVar: arg = BitConverter.ToInt16(il, i).ToString(); i += 2; break;
                        case OperandType.InlineI8: arg = BitConverter.ToInt64(il, i).ToString(); i += 8; break;
                        case OperandType.InlineR: arg = BitConverter.ToDouble(il, i).ToString(); i += 8; break;
                        case OperandType.ShortInlineR: arg = BitConverter.ToSingle(il, i).ToString(); i += 4; break;
                        case OperandType.InlineI: arg = BitConverter.ToInt32(il, i).ToString(); i += 4; break;
                        case OperandType.InlineBrTarget: arg = "IL_" + (i + 4 + BitConverter.ToInt32(il, i)).ToString("X4"); i += 4; break;
                        case OperandType.InlineSwitch: int n = BitConverter.ToInt32(il, i); i += 4; var bas = i + 4 * n; var tg = new List<string>(); for (int k = 0; k < n; k++) tg.Add("IL_" + (bas + BitConverter.ToInt32(il, i + 4 * k)).ToString("X4")); i = bas; arg = string.Join(",", tg); break;
                        default:
                            int tok = BitConverter.ToInt32(il, i); i += 4;
                            try
                            {
                                if (op == OpCodes.Ldstr) arg = "\"" + m.Module.ResolveString(tok).Replace("\n", "\\n") + "\"";
                                else if (op.OperandType == OperandType.InlineMethod) { var mb = m.Module.ResolveMethod(tok, gt, gm); arg = (mb.DeclaringType == null ? "" : mb.DeclaringType.Name) + "::" + mb.Name + "(" + string.Join(",", mb.GetParameters().Select(p => p.ParameterType.Name)) + ")"; if (mb is MethodInfo && ((MethodInfo)mb).IsGenericMethod) arg += "<" + string.Join(",", ((MethodInfo)mb).GetGenericArguments().Select(x => x.Name)) + ">"; }
                                else if (op.OperandType == OperandType.InlineField) { var fi = m.Module.ResolveField(tok, gt, gm); arg = fi.DeclaringType.Name + "::" + fi.Name; }
                                else if (op.OperandType == OperandType.InlineType) { arg = m.Module.ResolveType(tok, gt, gm).Name; }
                                else if (op.OperandType == OperandType.InlineTok) { var mm = m.Module.ResolveMember(tok, gt, gm); arg = mm.DeclaringType == null ? mm.Name : mm.DeclaringType.Name + "::" + mm.Name; }
                                else arg = "0x" + tok.ToString("X8");
                            }
                            catch { arg = "tok 0x" + tok.ToString("X8"); }
                            break;
                    }
                    Console.WriteLine("IL_" + start.ToString("X4") + ": " + op.Name + " " + arg);
                }
            }
        }
    }
}
