const fs = require('fs');
const html = fs.readFileSync('/home/yusupha/my_tools/nexus_audit/visuals/NEXUS_AUDIT_DASHBOARD.html', 'utf8');
const scriptMatch = html.match(/<script>([\s\S]*?)<\/script>/);
if (scriptMatch) {
    const script = scriptMatch[1];
    try {
        new Function(script);
        console.log("Syntax OK");
    } catch (e) {
        console.error(e);
    }
}
