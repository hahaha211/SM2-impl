# impl SM2 with RFC6979
# 加密流程
1. 在[1,n-1]任意选取k;
2. 计算椭圆曲线点C1=[k]G=(xi,yj);
3. 计算椭圆曲线点S=[h]PB,若S=0，报错退出。否则继续；
4. 计算[k]PB=(xi,yi);
5. 计算t=KDF(x2||y2,klen)(其中KDF为密钥生成函数，klen为待加密信息的长度)，若t=0，返回到第一步重新运行。否则继续；
6. 计算C2=M异或t;
7. 计算C3=Hash(x2||M||y2);
8. 输出密文C=C1||C2||C3。

# 解密流程
1. 从密文C中取出C1,验证C1是否满足椭圆曲线方程，如果不满足，则报错退出。否则继续；
2. 计算椭圆曲线点S=[h]C1,若S=0，报错退出。否则继续;
3. 计算椭圆曲线点(x2,y2)=[dB]C1;
4. 计算t=KDF(m2||y2,klen)，若t=0，则报错退出。否则继续；
5. 计算M'=C2异或t；
6. 计算u=Hash(x2||M'||y2),若u!=C3，则报错退出。否则继续；
7. 输出明文M'。

# 获取公私钥

![image](https://user-images.githubusercontent.com/71619888/181879727-2f0846d1-cbf0-4da9-bbed-f9bf165afca1.png)

# 代码分析

代码依照加解密流程逐步完善，细节请见代码注释。

# 实验结果

![KA3)S2)W2MSB3J @{BEEE43](https://user-images.githubusercontent.com/71619888/181902975-6feb5b6a-4fe4-49c6-baa2-f33d559dfc2f.png)

# 参考文献
https://blog.csdn.net/asdf_song/article/details/123480796
