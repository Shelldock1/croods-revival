import sys,os,struct,lzma
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
K=b'STcoQwkaTFyptI9F9CoSpHFxm3jTWqhe'
def un7z(b):
    assert b[:6]==b'7z\xbc\xaf\x27\x1c'
    off,size=struct.unpack_from('<QQ',b,12)
    packed=b[32:32+off]; hdr=b[32+off:32+off+size]
    if hdr[:1]==b'\x17':  # encoded header: decode it first (it is itself LZMA)
        raise ValueError('encoded header')
    i=hdr.find(b'\x03\x01\x01')
    props=hdr[i+4:i+9]
    lc=props[0]%9; lp=(props[0]//9)%5; pb=props[0]//45; dict_size=struct.unpack('<I',props[1:5])[0]
    filt=[{'id':lzma.FILTER_LZMA1,'dict_size':dict_size,'lc':lc,'lp':lp,'pb':pb}]
    d=lzma.LZMADecompressor(format=lzma.FORMAT_RAW,filters=filt)
    return d.decompress(packed)
def dec(path):
    ct=open(path,'rb').read()
    return un7z(Cipher(algorithms.AES(K),modes.CBC(b'\0'*16)).decryptor().update(ct))
if __name__=='__main__':
    src,dst=sys.argv[1],sys.argv[2]; ok=bad=0
    for root,_,files in os.walk(src):
        for f in files:
            if not f.endswith('.lua'): continue
            p=os.path.join(root,f); out=os.path.join(dst,os.path.relpath(p,src))
            os.makedirs(os.path.dirname(out),exist_ok=True)
            try: open(out,'wb').write(dec(p)); ok+=1
            except Exception as e: bad+=1; print('fail',p,e)
    print('ok',ok,'bad',bad)
