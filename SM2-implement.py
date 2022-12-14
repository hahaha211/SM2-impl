from gmssl import sm2
from random import SystemRandom
from base64 import b64encode, b64decode

#定义椭圆曲线
class EllCurve:
	def __init__(self, A, B, P, N, Gx, Gy, name):
		self.A = A
		self.B = B
		self.P = P
		self.N = N
		self.Gx = Gx
		self.Gy = Gy
		self.name = name


#初始化常量，选取SM2椭圆曲线公钥密码算法推荐曲线参数
sm2_class = EllCurve(
	name="sm2_class",
	A=0xFFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF00000000FFFFFFFFFFFFFFFC,
	B=0x28E9FA9E9D9F5E344D5A9E4BCF6509A7F39789F515AB8F92DDBCBD414D940E93,
	P=0xFFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF00000000FFFFFFFFFFFFFFFF,
	N=0xFFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFF7203DF6B21C6052B53BBF40939D54123,
	Gx=0x32C4AE2C1F1981195F9904466A39C9948FE30BBFF2660BE1715A4589334C74C7,
	Gy=0xBC3736A2F4F6779C59BDCEE36B692153D0A9877CC62A474002DF32E52139F0A0
)


#加解密过程中的主要函数


def mul(a, n, N, A, P):
	return CurveExc(CurveMul(CurveOne(a), n, N, A, P), P)


#返回值res=(n,n,1)
def CurveOne(n):
	x, y = n
	return (x, y, 1)

def CurveInv(a, n):
	if a == 0:
		return 0
	lm, hm = 1, 0
	low, high = a % n, n
	while low > 1:
		r = high//low
		nm, new = hm-lm*r, high-low*r
		lm, low, hm, high = nm, new, lm, low
	return lm % n

def CurveExc(n, P):
	X, Y, Z = n
	z = CurveInv(Z, P)
	return ((X * z**2) % P, (Y * z**3) % P)

#曲线点加
def CurveAdd(m, n, A, P):
	Xp, Yp, Zp = m
	Xq, Yq, Zq = n
	if not Yp:
		return (Xq, Yq, Zq)
	if not Yq:
		return (Xp, Yp, Zp)
	U1 = (Xp * Zq ** 2) % P
	U2 = (Xq * Zp ** 2) % P
	S1 = (Yp * Zq ** 3) % P
	S2 = (Yq * Zp ** 3) % P
	if U1 == U2:
		if S1 != S2:
			return (0, 0, 1)
		return CurveMath((Xp, Yp, Zp), A, P)
	H = U2 - U1
	R = S2 - S1
	H2 = (H * H) % P
	H3 = (H * H2) % P
	U1H2 = (U1 * H2) % P
	nx = (R ** 2 - H3 - 2 * U1H2) % P
	ny = (R * (U1H2 - nx) - S1 * H3) % P
	nz = (H * Zp * Zq) % P
	return (nx, ny, nz)

#曲线点乘
def CurveMul(m, n, N, A, P):
	X, Y, Z = m
	if Y == 0 or n == 0:
		return (0, 0, 1)
	if n == 1:
		return (X, Y, Z)
	if n < 0 or n >= N:
		return CurveMul((X, Y, Z), n % N, N, A, P)
	if (n % 2) == 0:
		return CurveMath(CurveMul((X, Y, Z), n // 2, N, A, P), A, P)
	if (n % 2) == 1:
		return CurveAdd(CurveMath(CurveMul((X, Y, Z), n // 2, N, A, P), A, P), (X, Y, Z), A, P)


def CurveMath(n, A, P):
	X, Y, Z = n
	if not Y:
		return (0, 0, 0)
	ysq = (Y ** 2) % P
	S = (4 * X * ysq) % P
	M = (3 * X ** 2 + A * Z ** 4) % P
	nx = (M**2 - 2 * S) % P
	ny = (M * (S - nx) - 8 * ysq ** 2) % P
	nz = (2 * Y * Z) % P
	return (nx, ny, nz)


#定义私钥的生成
class PK:
	def __init__(self, x, y, curve):
		self.x = x
		self.y = y
		self.curve = curve

	def tostring(self, compressed=True):
		return {
			True:  str(hex(self.x))[2:],
			False: "{}{}".format(str(hex(self.x))[2:].zfill(64), str(hex(self.y))[2:].zfill(64))
		}.get(compressed)

#定义公钥的生成
class SK:
	def __init__(self, curve=sm2_class, secret=None):
		self.curve = curve
		self.secret = secret or SystemRandom().randrange(1, curve.N)

	def publicKey(self):
		curve = self.curve
		xPublicKey, yPublicKey = mul((curve.Gx, curve.Gy), self.secret, A=curve.A, P=curve.P, N=curve.N)
		return PK(xPublicKey, yPublicKey, curve)

	def tostring(self):
		return "{}".format(str(hex(self.secret))[2:].zfill(64))

#关联公私钥的生成
priKey = SK()
pubKey = priKey.publicKey()


#定义SM2加解密（借用base64完成相应进制转化工作）
class sm2_1:
    def encrypt(self, info):
        encode_info = sm2_crypt.encrypt(info.encode(encoding="utf-8"))
        encode_info = b64encode(encode_info).decode()  
        return encode_info

    def decrypt(self, info):
        decode_info = b64decode(info.encode())
        decode_info = sm2_crypt.decrypt(decode_info).decode(encoding="utf-8")
        return decode_info


sm2_crypt = sm2.CryptSM2(public_key=pubKey.tostring(compressed = False), private_key=priKey.tostring())
sm2 = sm2_1()

if __name__=='__main__':
    m='This is a message'
    print("待加密的信息为 %s\n"%m)
    print("协商的私钥如下")
    print(priKey.tostring())
    print("\n协商的公钥如下")
    print(pubKey.tostring(compressed = False))
    # 加密的密码
    c = sm2.encrypt(m)
    print("\n加密得到的密文为\n%s"%c)
    # 解密的密码
    m1 = sm2.decrypt(c)
    print("\n解密得到的明文为 %s"%m1)
    if m1==m:
        print("\n算法正确！")
    else:
        print("算法错误")
    
