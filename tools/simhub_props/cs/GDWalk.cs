using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Text;

// Mimics SimHub DataCorePlugin.DeclareObject over a fresh StatusData instance.
// Usage: GDWalk.exe <simhubDir> <outDir>
class GDWalk
{
    static string dir;
    static StreamWriter w;
    static List<string> leafNames = new List<string>();
    static Dictionary<string, MemberInfo> leafMember = new Dictionary<string, MemberInfo>();

    static void Main(string[] a)
    {
        dir = a[0];
        AppDomain.CurrentDomain.AssemblyResolve += (s, e) =>
        {
            var n = new AssemblyName(e.Name).Name;
            foreach (var ext in new[] { ".dll", ".exe" }) { var p = Path.Combine(dir, n + ext); if (File.Exists(p)) try { return Assembly.UnsafeLoadFrom(p); } catch { } }
            return null;
        };
        var grc = Assembly.UnsafeLoadFrom(Path.Combine(dir, "GameReaderCommon.dll"));
        var sdGen = grc.GetType("GameReaderCommon.StatusData`1");
        var sd = sdGen.MakeGenericType(typeof(object));
        var gus = grc.GetTypes().FirstOrDefault(t => t.Name == "GameUnitSettings");
        object unit = null;
        try { unit = Activator.CreateInstance(gus); } catch { }
        object inst = null;
        foreach (var c in sd.GetConstructors())
        {
            var ps = c.GetParameters();
            try
            {
                if (ps.Length == 2) { inst = c.Invoke(new object[] { true, unit }); break; }
            }
            catch (Exception ex) { Console.WriteLine("ctor fail " + ex.InnerException); }
        }
        if (inst == null) inst = Activator.CreateInstance(sd);

        w = new StreamWriter(Path.Combine(a[1], "gamedata_walk.tsv"), false, new UTF8Encoding(false));
        w.WriteLine("name\talias\ttype\tattrs\tsample");
        DeclareObject(inst, "GameData", 0);
        w.Close();

        // Support matrix over all managers
        var managers = new List<Type>();
        foreach (var f in Directory.GetFiles(dir, "*.dll"))
        {
            var fn = Path.GetFileName(f);
            if (fn.StartsWith("System.") || fn.StartsWith("Microsoft.") || fn.StartsWith("CefSharp")) continue;
            try
            {
                AssemblyName.GetAssemblyName(f);
                var asm = Assembly.UnsafeLoadFrom(f);
                Type[] ts; try { ts = asm.GetTypes(); } catch (ReflectionTypeLoadException ex) { ts = ex.Types.Where(t => t != null).ToArray(); }
                foreach (var t in ts)
                {
                    try
                    {
                        if (t.IsAbstract || t.IsInterface || t.ContainsGenericParameters) continue;
                        if (t.GetInterfaces().Any(i => i.Name == "IGameManager")) managers.Add(t);
                    }
                    catch { }
                }
            }
            catch { }
        }
        var m = new StreamWriter(Path.Combine(a[1], "support_matrix.tsv"), false, new UTF8Encoding(false));
        var mi = new StreamWriter(Path.Combine(a[1], "managers.tsv"), false, new UTF8Encoding(false));
        var distinct = leafNames.Select(n => n.Split('.').Last()).Distinct().ToList();
        m.WriteLine("member\t" + string.Join("\t", managers.Select(t => t.FullName)));
        foreach (var name in distinct)
        {
            var row = new List<string> { name };
            MemberInfo mem = leafMember[name];
            foreach (var t in managers)
            {
                int st = 0;
                try
                {
                    var gd = t.GetMethod("GD_" + name, BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic);
                    if (gd == null) st = mem.GetCustomAttributes(false).Any(x => x.GetType().Name == "ComputedAttribute") ? 2 : 0;
                    else if (gd.GetCustomAttributes(false).Any(x => x.GetType().Name == "NotAvailableAttribute")) st = 1;
                    else if (gd.GetCustomAttributes(false).Any(x => x.GetType().Name == "ComputedAttribute")) st = 2;
                    else st = 0;
                    if (gd == null && st == 0) st = 9; // no GD_ method declared at all
                }
                catch (AmbiguousMatchException) { st = 8; }
                catch { st = 7; }
                row.Add(st.ToString());
            }
            m.WriteLine(string.Join("\t", row));
        }
        m.Close();
        foreach (var t in managers)
        {
            var bt = t.BaseType; var chain = new List<string>();
            while (bt != null && bt != typeof(object)) { chain.Add(Nm(bt)); bt = bt.BaseType; }
            var attrs = "";
            try { attrs = string.Join(" ; ", t.GetCustomAttributesData().Select(c => c.AttributeType.Name + "(" + string.Join(", ", c.ConstructorArguments.Select(x => x.Value == null ? "null" : x.Value.ToString())) + ")")); } catch { }
            mi.WriteLine(t.Assembly.GetName().Name + "\t" + t.FullName + "\t" + string.Join(" <- ", chain) + "\t" + attrs);
        }
        mi.Close();
    }

    static string Nm(Type t)
    {
        if (t.IsGenericType) return t.Name.Split('`')[0] + "<" + string.Join(",", t.GetGenericArguments().Select(Nm)) + ">";
        return t.FullName ?? t.Name;
    }

    static bool IsBasic(Type t)
    {
        var u = Nullable.GetUnderlyingType(t) ?? t;
        return u.IsPrimitive || u == typeof(string) || u == typeof(decimal) || u == typeof(DateTime) || u == typeof(DateTimeOffset) || u == typeof(TimeSpan) || u.IsEnum || (t.IsArray && false);
    }
    static bool Excluded(string n)
    {
        return n.Contains(".Skin") || n.EndsWith(".OldData") || n.EndsWith(".GameOldData") || n.EndsWith(".GameNewData") || n.EndsWith(".RawData") || n.EndsWith(".RawDataObject") || n.EndsWith(".Events");
    }
    static string Alias(string n)
    {
        if (!n.StartsWith("GameData.NewData.") && n.StartsWith("GameData.")) return n.Substring(9);
        return "";
    }
    static string AttrList(MemberInfo mi)
    {
        try
        {
            return string.Join(" ", mi.GetCustomAttributesData().Where(c => !c.AttributeType.Name.StartsWith("Compiler") && !c.AttributeType.Name.StartsWith("Debugger"))
                .Select(c => c.AttributeType.Name.Replace("Attribute", "") + (c.ConstructorArguments.Count > 0 ? "(" + string.Join(", ", c.ConstructorArguments.Select(x => x.Value == null ? "null" : x.Value.ToString())) + ")" : "")));
        }
        catch { return ""; }
    }
    static string Fmt(object v)
    {
        if (v == null) return "null";
        var s = Convert.ToString(v, System.Globalization.CultureInfo.InvariantCulture);
        return s.Replace("\t", " ").Replace("\n", " ");
    }

    static void DeclareObject(object value, string name, int depth)
    {
        if (value == null || depth > 12) return;
        if (Excluded(name)) return;
        var t = value.GetType();
        if (value is IDictionary)
        {
            foreach (DictionaryEntry kv in (IDictionary)value)
            {
                if (kv.Value != null && kv.Value.GetType().IsArray) continue;
                Emit(name + "." + kv.Key, kv.Value == null ? "object" : kv.Value.GetType().Name, "dict-key", kv.Value);
            }
            return;
        }
        if (t.IsArray)
        {
            var arr = (Array)value;
            for (int i = 0; i < arr.Length; i++) DeclareObject(arr.GetValue(i), string.Format("{0}{1:00}", name, i + 1), depth + 1);
            if (arr.Length == 0) Emit(name + "NN", t.Name, "array(empty in sample)", null);
            return;
        }
        if (typeof(IEnumerable).IsAssignableFrom(t)) return;
        if (IsBasic(t)) { Emit(name, t.Name, "", value); }
        var members = t.GetProperties(BindingFlags.Instance | BindingFlags.Public).Cast<MemberInfo>().Concat(t.GetFields(BindingFlags.Instance | BindingFlags.Public));
        foreach (var mem in members)
        {
            if (mem is PropertyInfo && ((PropertyInfo)mem).GetIndexParameters().Length > 0) continue;
            var attrs = mem.GetCustomAttributes(true).Select(x => x.GetType().Name).ToList();
            if (attrs.Contains("DoNotExposeAttribute")) continue;
            bool hidden = attrs.Contains("HiddenAttribute");
            var mt = mem is PropertyInfo ? ((PropertyInfo)mem).PropertyType : ((FieldInfo)mem).FieldType;
            string expName = mem.Name;
            var en = mem.GetCustomAttributesData().FirstOrDefault(c => c.AttributeType.Name == "ExposeNameAttribute");
            if (en != null && en.ConstructorArguments.Count > 0 && en.ConstructorArguments[0].Value != null && en.ConstructorArguments[0].Value.ToString() != "") expName = en.ConstructorArguments[0].Value.ToString();
            var full = name + "." + expName; if (Excluded(full)) continue;
            object v = null;
            try { v = mem is PropertyInfo ? ((PropertyInfo)mem).GetValue(value, null) : ((FieldInfo)mem).GetValue(value); } catch { }
            var at = AttrList(mem) + (hidden ? " HIDDEN" : "");
            if (IsBasic(mt))
            {
                Emit(full, TName(mt), at, v);
                leafNames.Add(full);
                if (!leafMember.ContainsKey(mem.Name)) leafMember[mem.Name] = mem;
            }
            else if (v == null)
            {
                Emit(full, TName(mt), at + " [null-in-sample: children only exist at runtime]", null);
                if (!leafMember.ContainsKey(mem.Name)) leafMember[mem.Name] = mem;
                leafNames.Add(full);
            }
            else DeclareObjectWithAttr(v, full, depth, at);
            foreach (var al in mem.GetCustomAttributesData().Where(c => c.AttributeType.Name == "ExposeAliasAttribute"))
                w.WriteLine("#ALIAS\t" + full + "\t" + string.Join(", ", al.ConstructorArguments.Select(x => x.Value)) + "\t" + string.Join(", ", al.NamedArguments.Select(x => x.MemberName + "=" + x.TypedValue.Value)));
        }
    }
    static void DeclareObjectWithAttr(object v, string full, int depth, string at)
    {
        if (at.Length > 0) w.WriteLine("#GROUP\t" + full + "\t" + at);
        DeclareObject(v, full, depth + 1);
    }
    static string TName(Type t)
    {
        var u = Nullable.GetUnderlyingType(t);
        if (u != null) return TName(u) + "?";
        if (t.IsGenericType) return t.Name.Split('`')[0] + "<" + string.Join(",", t.GetGenericArguments().Select(TName)) + ">";
        if (t.IsEnum) { try { return t.Name + "{" + string.Join(",", Enum.GetNames(t).Select(n => n + "=" + Convert.ToInt64(Enum.Parse(t, n)))) + "}"; } catch { } }
        return t.Name;
    }
    static void Emit(string name, string type, string attrs, object sample)
    {
        w.WriteLine(name + "\t" + Alias(name) + "\t" + type + "\t" + attrs + "\t" + Fmt(sample));
    }
}

