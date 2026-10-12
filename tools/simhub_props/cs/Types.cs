using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Text;

// Usage: Types.exe <simhubDir> <out.txt> <TypeFullName>[=prefix] ...
// Recursively walks public instance properties/fields of the given types and prints flattened paths with types.
class Types
{
    static string dir;
    static StreamWriter w;
    static void Main(string[] a)
    {
        dir = a[0];
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
        var all = new Dictionary<string, Type>();
        foreach (var f in Directory.GetFiles(dir, "*.dll").Concat(Directory.GetFiles(dir, "*.exe")))
        {
            var fn = Path.GetFileName(f);
            if (fn.StartsWith("System.") || fn.StartsWith("Microsoft.") || fn.StartsWith("CefSharp")) continue;
            try
            {
                AssemblyName.GetAssemblyName(f);
                var asm = Assembly.LoadFrom(f);
                Type[] ts; try { ts = asm.GetTypes(); } catch (ReflectionTypeLoadException ex) { ts = ex.Types.Where(t => t != null).ToArray(); }
                foreach (var t in ts) if (t.FullName != null && !all.ContainsKey(t.FullName)) all[t.FullName] = t;
            }
            catch { }
        }
        w = new StreamWriter(a[1], false, new UTF8Encoding(false));
        for (int i = 2; i < a.Length; i++)
        {
            var spec = a[i]; var parts = spec.Split('=');
            Type t;
            if (!all.TryGetValue(parts[0], out t)) { w.WriteLine("### NOT FOUND " + parts[0]); continue; }
            var prefix = parts.Length > 1 ? parts[1] : "";
            w.WriteLine("### " + t.AssemblyQualifiedName);
            Walk(t, prefix, 0, new HashSet<Type>());
            w.WriteLine();
        }
        w.Close();
    }
    static bool Leaf(Type t)
    {
        var u = Nullable.GetUnderlyingType(t) ?? t;
        return u.IsPrimitive || u.IsEnum || u == typeof(string) || u == typeof(decimal) || u == typeof(TimeSpan) || u == typeof(DateTime) || u == typeof(Guid) || u == typeof(object);
    }
    static string Name(Type t)
    {
        var u = Nullable.GetUnderlyingType(t);
        if (u != null) return Name(u) + "?";
        if (t.IsArray) return Name(t.GetElementType()) + "[]";
        if (t.IsGenericType) return t.Name.Split('`')[0] + "<" + string.Join(",", t.GetGenericArguments().Select(Name)) + ">";
        return t.Name;
    }
    static string EnumInfo(Type t)
    {
        var u = Nullable.GetUnderlyingType(t) ?? t;
        if (!u.IsEnum) return "";
        try
        {
            var names = Enum.GetNames(u);
            var vals = Enum.GetValues(u).Cast<object>().Select(v => Convert.ToInt64(v)).ToArray();
            return "  {" + string.Join(", ", names.Select((n, i) => n + "=" + vals[i])) + "}";
        }
        catch { return ""; }
    }
    static void Walk(Type t, string prefix, int depth, HashSet<Type> seen)
    {
        if (depth > 6 || seen.Contains(t)) { w.WriteLine(prefix + "  : " + Name(t) + " (recursion)"); return; }
        seen = new HashSet<Type>(seen); seen.Add(t);
        var members = new List<KeyValuePair<string, Type>>();
        try
        {
            foreach (var p in t.GetProperties(BindingFlags.Public | BindingFlags.Instance))
                if (p.GetIndexParameters().Length == 0 && !members.Any(m => m.Key == p.Name)) members.Add(new KeyValuePair<string, Type>(p.Name, p.PropertyType));
            foreach (var f in t.GetFields(BindingFlags.Public | BindingFlags.Instance))
                if (!members.Any(m => m.Key == f.Name)) members.Add(new KeyValuePair<string, Type>(f.Name, f.FieldType));
        }
        catch (Exception ex) { w.WriteLine(prefix + " !! " + ex.Message); return; }
        foreach (var m in members)
        {
            var path = prefix.Length == 0 ? m.Key : prefix + "." + m.Key;
            var mt = m.Value;
            if (Leaf(mt)) { w.WriteLine(path + "\t" + Name(mt) + EnumInfo(mt)); continue; }
            if (mt.IsArray)
            {
                var et = mt.GetElementType();
                w.WriteLine(path + "\t" + Name(mt));
                if (!Leaf(et)) Walk(et, path + "[i]", depth + 1, seen);
                continue;
            }
            if (mt.IsGenericType && typeof(System.Collections.IEnumerable).IsAssignableFrom(mt))
            {
                w.WriteLine(path + "\t" + Name(mt));
                var ga = mt.GetGenericArguments();
                var et = ga[ga.Length - 1];
                if (!Leaf(et)) Walk(et, path + "[i]", depth + 1, seen);
                continue;
            }
            if (typeof(System.Collections.IEnumerable).IsAssignableFrom(mt) || mt.Namespace != null && (mt.Namespace.StartsWith("System") || mt.Namespace.StartsWith("Newtonsoft")))
            { w.WriteLine(path + "\t" + Name(mt)); continue; }
            w.WriteLine(path + "\t" + Name(mt));
            Walk(mt, path, depth + 1, seen);
        }
    }
}
