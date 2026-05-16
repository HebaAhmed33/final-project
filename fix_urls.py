import os

files = [
    r"c:\new project\frontend\app\exports\page.js",
    r"c:\new project\frontend\app\page.js",
    r"c:\new project\frontend\app\configuration\upload\page.js",
    r"c:\new project\frontend\app\upload\page.js",
    r"c:\new project\frontend\app\admin\clients\page.js",
]

for fpath in files:
    if not os.path.exists(fpath):
        continue
    with open(fpath, "r", encoding="utf-8") as f:
        content = f.read()
    
    if "http://localhost:8000" in content:
        # Check if API_BASE_URL import is missing
        if "API_BASE_URL" not in content[:content.find("export default")]:
            depth = fpath.count("\\") - r"c:\new project\frontend\app".count("\\")
            import_path = "../" * (depth - 1) + "lib/api" if depth > 1 else "../lib/api"
            if fpath == r"c:\new project\frontend\app\page.js":
                import_path = "./lib/api"
                
            import_stmt = f'import API_BASE_URL from "{import_path}";\n'
            
            if '"use client";' in content:
                content = content.replace('"use client";', f'"use client";\n{import_stmt}', 1)
            elif "'use client';" in content:
                content = content.replace("'use client';", f"'use client';\n{import_stmt}", 1)
            else:
                content = import_stmt + content

        # Replace usages
        content = content.replace("`http://localhost:8000/", "`${API_BASE_URL}/")
        content = content.replace("\"http://localhost:8000/", "`${API_BASE_URL}/")
        content = content.replace("'http://localhost:8000/", "`${API_BASE_URL}/")
        content = content.replace("http://localhost:8000", "${API_BASE_URL}")

        with open(fpath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Fixed {fpath}")
