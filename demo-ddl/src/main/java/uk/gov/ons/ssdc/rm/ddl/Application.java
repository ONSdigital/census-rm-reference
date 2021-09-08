package uk.gov.ons.ssdc.rm.ddl;

import java.io.File;
import java.io.FileInputStream;
import java.util.ArrayList;
import java.util.EnumSet;
import java.util.List;
import java.util.jar.JarEntry;
import java.util.jar.JarInputStream;
import org.hibernate.boot.MetadataSources;
import org.hibernate.boot.registry.StandardServiceRegistryBuilder;
import org.hibernate.boot.spi.MetadataImplementor;
import org.hibernate.dialect.PostgreSQL94Dialect;
import org.hibernate.tool.hbm2ddl.SchemaExport;
import org.hibernate.tool.schema.TargetType;

public class Application {

  private static final String OUTPUT_DIRECTORY = "groundzero_ddl";

  public static void main(String[] args) {
    try {
      generate(PostgreSQL94Dialect.class, args[0], args[1]);
    } catch (Exception e) {
      e.printStackTrace();
    }
  }

  private static void generate(Class dialect, String schemaName, String... packagesName) {

    MetadataSources metadata = new MetadataSources(
        new StandardServiceRegistryBuilder()
            .applySetting("hibernate.dialect", dialect.getName())
            .build());

    for (String packageName : packagesName) {
      System.out.println("packageName: " + packageName);
      for (Class clazz : getClasses(packageName)) {
        System.out.println("Class: " + clazz);
        metadata.addAnnotatedClass(clazz);
      }
    }

    MetadataImplementor metadataImplementor = (MetadataImplementor) metadata.buildMetadata();
    SchemaExport export = new SchemaExport();

    export.setDelimiter(";");
    String filename = OUTPUT_DIRECTORY + "/" + schemaName + ".sql";
    export.setOutputFile(filename);
    export.setFormat(true);

    //can change the output here
    EnumSet<TargetType> enumSet = EnumSet.of(TargetType.SCRIPT);
    export.execute(enumSet, SchemaExport.Action.CREATE, metadataImplementor);
  }

  public static final List<Class<?>> getClasses(String packageName) {
    String path = packageName.replaceAll("\\.", File.separator);
    List<Class<?>> classes = new ArrayList<>();
    String[] classPathEntries = System.getProperty("java.class.path").split(
        System.getProperty("path.separator")
    );

    String name;
    for (String classpathEntry : classPathEntries) {
      if (classpathEntry.endsWith(".jar")) {
        File jar = new File(classpathEntry);
        try {
          JarInputStream is = new JarInputStream(new FileInputStream(jar));
          JarEntry entry;
          while ((entry = is.getNextJarEntry()) != null) {
            name = entry.getName();
            if (name.endsWith(".class")) {
              if (name.contains(path) && name.endsWith(".class")) {
                String classPath = name.substring(0, entry.getName().length() - 6);
                classPath = classPath.replaceAll("[\\|/]", ".");
                try {
                  classes.add(Class.forName(classPath));
                } catch (NoClassDefFoundError ex) {
                  // Ignored
                }
              }
            }
          }
        } catch (Exception ex) {
          // Silence is gold
        }
      } else {
        try {
          File base = new File(classpathEntry + File.separatorChar + path);
          for (File file : base.listFiles()) {
            name = file.getName();
            if (name.endsWith(".class")) {
              name = name.substring(0, name.length() - 6);
              classes.add(Class.forName(packageName + "." + name));
            }
          }
        } catch (Exception ex) {
          // Silence is gold
        }
      }
    }

    return classes;
  }
}
