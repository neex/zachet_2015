#include <stdio.h>
#include "midcrypt_cpp.cpp"
#include <map>
#include <string.h>
#include <algorithm>

unsigned char possible [0x1000000][19];

unsigned char lastb[256];

unsigned char unsbox[256];

int idxs[0x1000000];

int decrypt_init() {
    for (int i = 0; i < 256; ++i) {
        unsbox[sbox[i]] = i;        
    }

    for (int xx = 0; xx < 256; ++xx) {
        unsigned char x = xx;
        for (int r = 0; r < 100; ++r) {
            for (int i = 0; i < 16; ++i) {
                x = x * 5 + 1;
            }
        }
        lastb[xx] = x;        
    }
 
}

void decrypt_midcrypt(unsigned char key[6], unsigned char in_[16], unsigned char out[16]) {
    decrypt_init();
    
    for (int i = 0; i < 16; ++i) {
        out[i] = in_[i];
    }
    
    for (int k = 5; k >= 0; --k) {
        unsigned char x = lastb[key[k]];
        for (int r = 0; r < 100; ++r) {                
            int last = out[15];
            for (int i = 15; i > 0; --i) {
                out[i] = (out[i] >> 3) ^ (out[i - 1] << 5);
            }
            out[0] = (out[0] >> 3) ^ (last << 5);
            
            for (int i = 15; i >= 0; --i) {
                out[i] = unsbox[out[i]];                       
                out[i] ^= x;                    
                x = (x - 1) * 205;                    
            }
            
        }
    }

}

int test_hack() {

    decrypt_init();
    
    //    char key[7] = "0sHjzk";
    char plain1[17] = "1234567890123456";
    unsigned char crypt1[16] = {0xb5, 0xf0, 0xe2, 0xee, 0x6, 0x66, 0x30, 0xc3, 0xa9, 0x3, 0xa5, 0x6a,
                                0x81, 0xbb, 0xb7, 0x5f};

    //    midcrypt((unsigned char*) key, (unsigned char*) plain1, (unsigned char*) crypt1);

    unsigned char tk[3];
    unsigned char out[16];
    unsigned char prev2[16];
    
    for (int try_key = 0; try_key < 0x1000000; ++try_key) {
        if ((try_key & 0xffff) == 0) {
            printf("First part of key: %06x\n", try_key);
        }
        tk[2] = try_key & 255;
        tk[1] = (try_key >> 8) & 255;
        tk[0] = (try_key >> 16) & 255;

        for (int i = 0; i < 16; ++i) {
            out[i] = tk[2] ? prev2[i] : plain1[i];
        }
        
        for (int k = tk[2] ? 2 : 0; k < 3; ++k) {
            unsigned char x = tk[k];
            for (int r = 0; r < 100; ++r) {
                
                for (int i = 0; i < 16; ++i) {
                    x = x * 5 + 1;
                    out[i] ^= x;
                    out[i] = sbox[out[i]];
                }
                
                unsigned char first = out[0];
                for (int i = 0; i < 15; ++i) {
                    out[i] = (out[i] << 3) ^ (out[i+1] >> 5);
               }
                out[15] = (out[15] << 3) ^ (first >> 5);
                
            }
            if (k == 1) {
                memcpy(prev2, out, 16);
            }
        }        
        memcpy(possible[try_key], out, 16);
        memcpy(possible[try_key] + 16, tk, 3);
    }

    for (int i = 0; i < 0x1000000; ++i) {
        idxs[i] = i;
    }
    
    printf("Sorting... \n");
    std::sort(idxs, idxs + 0x1000000, [] (int i, int j) { return memcmp(possible[i], possible[j], 16) < 0; });

    for (int try_key = 0; try_key < 0x1000000; ++try_key) {
        if ((try_key & 0xffff) == 0) {            
            printf("Second part of key: %06x\n", try_key);
        }
        tk[0] = try_key & 255;
        tk[1] = (try_key >> 8) & 255;
        tk[2] = (try_key >> 16) & 255;

        for (int i = 0; i < 16; ++i) {
            out[i] = crypt1[i];
        }
        
        for (int k = 2; k >= 0; --k) {
            unsigned char x = lastb[tk[k]];
            for (int r = 0; r < 100; ++r) {                
                int last = out[15];
                for (int i = 15; i > 0; --i) {
                    out[i] = (out[i] >> 3) ^ (out[i - 1] << 5);
                }
                out[0] = (out[0] >> 3) ^ (last << 5);
                                
                for (int i = 15; i >= 0; --i) {
                    out[i] = unsbox[out[i]];                       
                    out[i] ^= x;                    
                    x = (x - 1) * 205;                    
                }
                
            }
        }
        
        int ll = 0;
        int rr = 0x1000000;
        while (rr - ll > 1) {
            int t = (ll + rr) / 2;
            int c = memcmp(out, possible[idxs[t]], 16);
            if (c == 0) {
                printf("found possible key: ");
                for (int i = 0; i < 3; ++i) {
                    printf("%02x ", (int) possible[idxs[t]][16 + i]);
                }

                for (int i = 0; i < 3; ++i) {
                    printf("%02x ", (int) tk[i]);
                }
                printf("\n");
                
            }
            if (c < 0) {
                rr = t;
            } else {
                ll = t;
            }
        }
    }
}

int test_crypt() {
    unsigned char key[7] = "THEkey";
    unsigned char plain[17] = "it's a test text";
    unsigned char crypted[17];
    midcrypt(key, plain, crypted);
    for (int i = 0; i < 16; ++i) {
        printf("%02x ", crypted[i]);
    }
    printf("\n");
}

int test_decrypt() {
    unsigned char key[6] = {0x8d, 0x0f, 0x2b, 0x0b, 0xd8, 0x7d};
    unsigned char in[17] = {0xd8, 0xf6, 0x1c, 0x56, 0x8b, 0x70, 0xba, 0xca, 0x8, 0xad, 0xf7, 0x8f,
                                0xcf, 0xb1, 0x75, 0x2};
    unsigned char out[17];
    decrypt_midcrypt(key, in, out);
    out[16] = 0;
    printf("%s\n", out);
        
}
int main() {
    test_decrypt();
}
