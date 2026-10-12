using System;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Text;
using System.Text.RegularExpressions;

// Usage: Members.exe <simhubDir> <assemblyFile> <typeRegex> [all]
class Members
{
    static void Main(string[] a)
    {
        var dir = a[0];
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
        var asm = Assembly.LoadFrom(Path.Combine(dir, a[1]));
        Type[] ts; try { ts = asm.GetTypes(); } catch (ReflectionTypeLoadException ex) { ts = ex.Types.Where(t => t != null).ToArray(); }
        var rx = new Regex(a[2]);
        bool all = a.Length > 3;
        var fl = BindingFlags.Public | BindingFlags.Instance | BindingFlags.Static | BindingFlags.DeclaredOnly;
        if (all) fl |= BindingFlags.NonPublic;
        foreach (var t in ts.Where(t => t.FullName != null && rx.IsMatch(t.FullName)).OrderBy(t => t.FullName))
        {
            Console.WriteLine("TYPE " + t.FullName + " : " + (t.BaseType == null ? "" : t.BaseType.Name) + Attrs(t.GetCustomAttributesData()));
            if (t.IsEnum)
            {
                foreach (var n in Enum.GetNames(t)) Console.WriteLine("  " + n + " = " + Convert.ToInt64(Enum.Parse(t, n)));
                continue;
            }
            try
            {
                foreach (var m in t.GetMethods(fl).Where(m => !m.IsSpecialName))
                    Console.WriteLine("  M " + (m.IsStatic ? "static " : "") + N(m.ReturnType) + " " + m.Name + "(" + string.Join(", ", m.GetParameters().Select(p => N(p.ParameterType) + " " + p.Name)) + ")" + Attrs(m.GetCustomAttributesData()));
                foreach (var p in t.GetProperties(fl))
                    Console.WriteLine("  P " + N(p.PropertyType) + " " + p.Name + Attrs(p.GetCustomAttributesData()));
                foreach (var f in t.GetFields(fl))
                    Console.WriteLine("  F " + N(f.FieldType) + " " + f.Name + (f.IsLiteral ? " = " + f.GetRawConstantValue() : ""));
            }
            catch (Exception ex) { Console.WriteLine("  !! " + ex.Message); }
        }
    }
    static string N(Type t)
    {
        if (t.IsGenericType) return t.Name.Split('`')[0] + "<" + string.Join(",", t.GetGenericArguments().Select(N)) + ">";
        return t.Name;
    }
    static string Attrs(System.Collections.Generic.IList<CustomAttributeData> l)
    {
        try
        {
            var s = l.Where(c => !c.AttributeType.Name.StartsWith("Compiler") && !c.AttributeType.Name.StartsWith("Debugger"))
                .Select(c => c.AttributeType.Name.Replace("Attribute", "") + "(" + string.Join(", ", c.ConstructorArguments.Select(x => x.Value == null ? "null" : x.Value.ToString())) + ")");
            var j = string.Join(" ", s);
            return j.Length > 0 ? "   [" + j + "]" : "";
        }
        catch { return ""; }
    }
}
