import markdown
import re

md_file = open('README.md', 'r', encoding='utf-8')
s = '''<style>
    .push-cont-wrap {word-break: normal;border: none; white-space: normal;}
    table {
    width: 100%;
    max-width: 65em;
    border: 1px solid #dedede;
    margin: 15px auto;
    border-collapse: collapse;
    empty-cells: show;
    }
    .table-area {
        overflow: auto;
    }
table th, table td {
  height: 35px;
  border: 1px solid #dedede;
  padding: 0 10px;
}
table th {
    font-weight: bold;
    text-align: center !important;
    background: rgba(255, 121, 121,1.0);
}
table tbody tr:nth-child(2n) {
    background: rgba(255, 121, 121,0.3);
}
table tr:hover {
    background: #efefef;
}
table th {
    white-space: nowrap;
}
table td:nth-child(1) {
    white-space: nowrap;
}
</style>'''
s += md_file.read()
html = markdown.markdown(s, output_format='html5', extensions=['markdown.extensions.tables'])
html = re.sub(r' align=".*?"', r'', html)
output = open('推送.html', 'w', encoding='utf-8')
output.write(html)
