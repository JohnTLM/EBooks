import zipfile, uuid, re, sys
src, dst = sys.argv[1], sys.argv[2]
import os
FD = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fonts', 'GentiumBookPlus-%s.ttf')
styles = [('Regular','embedRegular'),('Bold','embedBold'),('Italic','embedItalic'),('BoldItalic','embedBoldItalic')]
zin = zipfile.ZipFile(src)
files = {n: zin.read(n) for n in zin.namelist()}
rels = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">']
embeds = []
for i,(st,tag) in enumerate(styles, 1):
    key = str(uuid.uuid4()).upper()
    k = [int(x,16) for x in re.findall('..', key.replace('-',''))][::-1]
    data = bytearray(open(FD % st,'rb').read())
    for j in range(32): data[j] ^= k[j % 16]
    files['word/fonts/font%d.odttf' % i] = bytes(data)
    rels.append('<Relationship Id="rIdF%d" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/font" Target="fonts/font%d.odttf"/>' % (i,i))
    embeds.append('<w:%s r:id="rIdF%d" w:fontKey="{%s}"/>' % (tag, i, key))
mono=bytearray(open('/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf','rb').read())
mkey=str(uuid.uuid4()).upper(); mk=[int(x,16) for x in re.findall('..', mkey.replace('-',''))][::-1]
for j in range(32): mono[j]^=mk[j%16]
files['word/fonts/font5.odttf']=bytes(mono)
rels.append('<Relationship Id="rIdF5" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/font" Target="fonts/font5.odttf"/>')
rels.append('</Relationships>')
files['word/_rels/fontTable.xml.rels'] = '\n'.join(rels).encode()
ft = files['word/fontTable.xml'].decode()
font_el = ('<w:font w:name="Gentium Book Plus"><w:charset w:val="00"/><w:family w:val="roman"/><w:pitch w:val="variable"/>'
           + ''.join(embeds) + '</w:font>'
           + '<w:font w:name="DejaVu Sans Mono"><w:charset w:val="00"/><w:family w:val="modern"/><w:pitch w:val="fixed"/>'
           + '<w:embedRegular r:id="rIdF5" w:fontKey="{%s}"/></w:font>' % mkey)
ft = re.sub(r'<w:font w:name="Gentium Book Plus".*?</w:font>', '', ft, flags=re.S)
if 'xmlns:r=' not in ft.split('>',2)[1]:
    ft = ft.replace('<w:fonts ', '<w:fonts xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" ', 1)
if re.search(r'<w:fonts[^>]*/>', ft):
    ft = re.sub(r'<w:fonts([^>]*)/>', lambda m: '<w:fonts' + m.group(1) + '>' + font_el + '</w:fonts>', ft, count=1)
else:
    ft = re.sub(r'(<w:fonts[^>]*>)', lambda m: m.group(1) + font_el, ft, count=1)
files['word/fontTable.xml'] = ft.encode()
ct = files['[Content_Types].xml'].decode()
if 'odttf' not in ct:
    ct = ct.replace('<Default ', '<Default Extension="odttf" ContentType="application/vnd.openxmlformats-officedocument.obfuscatedFont"/><Default ', 1)
files['[Content_Types].xml'] = ct.encode()
st = files['word/settings.xml'].decode()
if 'embedTrueTypeFonts' not in st:
    st = st.replace('<w:displayBackgroundShape/>', '<w:displayBackgroundShape/><w:embedTrueTypeFonts/>', 1) if '<w:displayBackgroundShape/>' in st else re.sub(r'(<w:settings[^>]*>)', lambda m: m.group(1) + '<w:embedTrueTypeFonts/>', st, count=1)
st = st.replace('<w:evenAndOddHeaders w:val="false"/>', '')
st = st.replace('<w:hyphenationZone w:val="357"/><w:consecutiveHyphenLimit w:val="2"/>', '<w:consecutiveHyphenLimit w:val="2"/><w:hyphenationZone w:val="357"/>')
files['word/settings.xml'] = st.encode()
with zipfile.ZipFile(dst, 'w', zipfile.ZIP_DEFLATED) as z:
    order = ['[Content_Types].xml'] + [n for n in files if n != '[Content_Types].xml']
    for n in order: z.writestr(n, files[n])
print('embedded', len(embeds))
