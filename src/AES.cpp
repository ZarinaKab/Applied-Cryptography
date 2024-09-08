#pragma once

#include <algorithm>
#include <iostream>
#include <vector>
#include <array>

namespace AES {
    class Poly{
        /*
            Realization of Extension Galois Fields(2^8) arithmetic under 
            irreducible polynomial P(x) = x^8 + x^4 + x^3 + x + 1.
            Store polinomial coefficients a_7*x^7 + ... a_0*x^0 as bitstring in byte.
        */
        unsigned char x;
        const static unsigned char P = 0b0001'1011; // Reduced P(x) - without x^8
    public:
        Poly(): x(0) {}
        constexpr Poly(unsigned char _x): x(_x) {}

        constexpr friend Poly operator+(Poly a, Poly b){ return a.x^b.x; }
        constexpr friend Poly operator-(Poly a, Poly b){ return a.x^b.x; }
        constexpr friend Poly operator*(Poly a, Poly b){
            unsigned char res = 0;
            while(b.x){
                if (b.x & 1) // if coefficient at x^0 active, we need to add a to result
                    res ^= a.x;

                bool was_msb = (a.x & (1 << 7));
                a.x <<= 1; // multiply by x
                if (was_msb) // if coefficient at x^7 was active, we need to reduce a
                    a.x ^= P;

                b.x >>= 1; // divide by x
            }
            return res;
        }

        constexpr Poly& operator+=(Poly a){ return *this = *this + a; }
        constexpr Poly& operator-=(Poly a){ return *this = *this - a; }
        constexpr Poly& operator*=(Poly a){ return *this = *this * a; }
        constexpr bool  operator!=(Poly a){ return this->x != a.x; }

        constexpr Poly inv(){
            if (this->x == 0) return 0;
            // Naive method for finding inverse in field
            for(Poly pos(255); pos.x > 0; pos.x--){
                if ((pos * *this).x == 1){
                    return pos;
                }
            }
            return 0;
        }

        constexpr explicit operator unsigned char() const { return x; }
        constexpr explicit operator int() const { return x; }

        friend std::ostream& operator<<(std::ostream& out, Poly a){
            // Function to cout Poly
            const static char hex[] = "0123456789ABCDEF";
            out << hex[a.x >> 4] << hex[a.x & 0b1111];
            return out;
        }
    };

    // Substitution tables
    constexpr Poly S_BOX[256] = {
        0x63, 0x7c, 0x77, 0x7b, 0xf2, 0x6b, 0x6f, 0xc5, 0x30, 0x01, 0x67, 0x2b, 0xfe, 0xd7, 0xab, 0x76,
        0xca, 0x82, 0xc9, 0x7d, 0xfa, 0x59, 0x47, 0xf0, 0xad, 0xd4, 0xa2, 0xaf, 0x9c, 0xa4, 0x72, 0xc0,
        0xb7, 0xfd, 0x93, 0x26, 0x36, 0x3f, 0xf7, 0xcc, 0x34, 0xa5, 0xe5, 0xf1, 0x71, 0xd8, 0x31, 0x15,
        0x04, 0xc7, 0x23, 0xc3, 0x18, 0x96, 0x05, 0x9a, 0x07, 0x12, 0x80, 0xe2, 0xeb, 0x27, 0xb2, 0x75,
        0x09, 0x83, 0x2c, 0x1a, 0x1b, 0x6e, 0x5a, 0xa0, 0x52, 0x3b, 0xd6, 0xb3, 0x29, 0xe3, 0x2f, 0x84,
        0x53, 0xd1, 0x00, 0xed, 0x20, 0xfc, 0xb1, 0x5b, 0x6a, 0xcb, 0xbe, 0x39, 0x4a, 0x4c, 0x58, 0xcf,
        0xd0, 0xef, 0xaa, 0xfb, 0x43, 0x4d, 0x33, 0x85, 0x45, 0xf9, 0x02, 0x7f, 0x50, 0x3c, 0x9f, 0xa8,
        0x51, 0xa3, 0x40, 0x8f, 0x92, 0x9d, 0x38, 0xf5, 0xbc, 0xb6, 0xda, 0x21, 0x10, 0xff, 0xf3, 0xd2,
        0xcd, 0x0c, 0x13, 0xec, 0x5f, 0x97, 0x44, 0x17, 0xc4, 0xa7, 0x7e, 0x3d, 0x64, 0x5d, 0x19, 0x73,
        0x60, 0x81, 0x4f, 0xdc, 0x22, 0x2a, 0x90, 0x88, 0x46, 0xee, 0xb8, 0x14, 0xde, 0x5e, 0x0b, 0xdb,
        0xe0, 0x32, 0x3a, 0x0a, 0x49, 0x06, 0x24, 0x5c, 0xc2, 0xd3, 0xac, 0x62, 0x91, 0x95, 0xe4, 0x79,
        0xe7, 0xc8, 0x37, 0x6d, 0x8d, 0xd5, 0x4e, 0xa9, 0x6c, 0x56, 0xf4, 0xea, 0x65, 0x7a, 0xae, 0x08,
        0xba, 0x78, 0x25, 0x2e, 0x1c, 0xa6, 0xb4, 0xc6, 0xe8, 0xdd, 0x74, 0x1f, 0x4b, 0xbd, 0x8b, 0x8a,
        0x70, 0x3e, 0xb5, 0x66, 0x48, 0x03, 0xf6, 0x0e, 0x61, 0x35, 0x57, 0xb9, 0x86, 0xc1, 0x1d, 0x9e,
        0xe1, 0xf8, 0x98, 0x11, 0x69, 0xd9, 0x8e, 0x94, 0x9b, 0x1e, 0x87, 0xe9, 0xce, 0x55, 0x28, 0xdf,
        0x8c, 0xa1, 0x89, 0x0d, 0xbf, 0xe6, 0x42, 0x68, 0x41, 0x99, 0x2d, 0x0f, 0xb0, 0x54, 0xbb, 0x16
    };
    
    constexpr Poly INV_S_BOX[256] = {
        0x52, 0x09, 0x6a, 0xd5, 0x30, 0x36, 0xa5, 0x38, 0xbf, 0x40, 0xa3, 0x9e, 0x81, 0xf3, 0xd7, 0xfb,
        0x7c, 0xe3, 0x39, 0x82, 0x9b, 0x2f, 0xff, 0x87, 0x34, 0x8e, 0x43, 0x44, 0xc4, 0xde, 0xe9, 0xcb,
        0x54, 0x7b, 0x94, 0x32, 0xa6, 0xc2, 0x23, 0x3d, 0xee, 0x4c, 0x95, 0x0b, 0x42, 0xfa, 0xc3, 0x4e,
        0x08, 0x2e, 0xa1, 0x66, 0x28, 0xd9, 0x24, 0xb2, 0x76, 0x5b, 0xa2, 0x49, 0x6d, 0x8b, 0xd1, 0x25,
        0x72, 0xf8, 0xf6, 0x64, 0x86, 0x68, 0x98, 0x16, 0xd4, 0xa4, 0x5c, 0xcc, 0x5d, 0x65, 0xb6, 0x92,
        0x6c, 0x70, 0x48, 0x50, 0xfd, 0xed, 0xb9, 0xda, 0x5e, 0x15, 0x46, 0x57, 0xa7, 0x8d, 0x9d, 0x84,
        0x90, 0xd8, 0xab, 0x00, 0x8c, 0xbc, 0xd3, 0x0a, 0xf7, 0xe4, 0x58, 0x05, 0xb8, 0xb3, 0x45, 0x06,
        0xd0, 0x2c, 0x1e, 0x8f, 0xca, 0x3f, 0x0f, 0x02, 0xc1, 0xaf, 0xbd, 0x03, 0x01, 0x13, 0x8a, 0x6b,
        0x3a, 0x91, 0x11, 0x41, 0x4f, 0x67, 0xdc, 0xea, 0x97, 0xf2, 0xcf, 0xce, 0xf0, 0xb4, 0xe6, 0x73,
        0x96, 0xac, 0x74, 0x22, 0xe7, 0xad, 0x35, 0x85, 0xe2, 0xf9, 0x37, 0xe8, 0x1c, 0x75, 0xdf, 0x6e,
        0x47, 0xf1, 0x1a, 0x71, 0x1d, 0x29, 0xc5, 0x89, 0x6f, 0xb7, 0x62, 0x0e, 0xaa, 0x18, 0xbe, 0x1b,
        0xfc, 0x56, 0x3e, 0x4b, 0xc6, 0xd2, 0x79, 0x20, 0x9a, 0xdb, 0xc0, 0xfe, 0x78, 0xcd, 0x5a, 0xf4,
        0x1f, 0xdd, 0xa8, 0x33, 0x88, 0x07, 0xc7, 0x31, 0xb1, 0x12, 0x10, 0x59, 0x27, 0x80, 0xec, 0x5f,
        0x60, 0x51, 0x7f, 0xa9, 0x19, 0xb5, 0x4a, 0x0d, 0x2d, 0xe5, 0x7a, 0x9f, 0x93, 0xc9, 0x9c, 0xef,
        0xa0, 0xe0, 0x3b, 0x4d, 0xae, 0x2a, 0xf5, 0xb0, 0xc8, 0xeb, 0xbb, 0x3c, 0x83, 0x53, 0x99, 0x61,
        0x17, 0x2b, 0x04, 0x7e, 0xba, 0x77, 0xd6, 0x26, 0xe1, 0x69, 0x14, 0x63, 0x55, 0x21, 0x0c, 0x7d
    };

    // matrices for mix columns stage
    const Poly MIX_COL_MAT[4][4] = {{2, 3, 1, 1}, {1, 2, 3, 1}, {1, 1, 2, 3}, {3, 1, 1, 2}};

    const Poly INV_MIX_COL_MAT[4][4] = {{14, 11, 13, 9}, {9, 14, 11, 13}, {13, 9, 14, 11}, {11, 13, 9, 14}};

    constexpr Poly get_S_box_value(unsigned char ind){
        const unsigned char matrix[8] = {
            0b1111'0001,
            0b1110'0011,
            0b1100'0111,
            0b1000'1111,
            0b0001'1111,
            0b0011'1110,
            0b0111'1100,
            0b1111'1000,
        };
        const unsigned char add_vector = 0b0110'0011;

        unsigned char inverse = (unsigned char)(Poly(ind).inv());
        unsigned char result = 0;
        for(int i = 0; i < 8; i++){
            unsigned char row = matrix[i] & inverse;
            /*
                As we have bit matrix-vector multiplication, we should do addition in GF(2),
                simply result[i] = cound_1_bits(row)%2
            */
            for(int j = 0; j < 8; j++){
                if (row & (1 << j)) result ^= (1 << i);
            }
        }
        result ^= add_vector;
        return result;
    }

    constexpr bool check_S_box(){
        for (unsigned char ind = 0; ; ind++){
            Poly need = get_S_box_value(ind);
            if (need != S_BOX[ind]) {
                std::cerr << ind << ' ' << need << ' ' << S_BOX[ind] << '\n';
                return false;
            }
            if (ind == 255) break;
        }
        for (unsigned char ind = 0; ; ind++){
            /*
                As inverse S-box is simply inverse permutation of 
                the original S-box, we can check it in the following way.
            */
            if (Poly(ind) != S_BOX[(int)INV_S_BOX[ind]]) {
                return false;
            }
            if (ind == 255) break;
        }
        return true;
    }

    static_assert(check_S_box());

    template<class State>
    class ECB{
    public:
        ECB(const State& iv){}
        void encrypt(State& block, const State keys[]){
            block.encrypt(keys);
        }
        void decrypt(State& block, const State keys[]){
            block.decrypt(keys);
        }
    };

    template<class State>
    class CBC{
        State internal;
    public:
        CBC(const State& iv){ internal = iv; }
        void encrypt(State& block, const State keys[]){
            block ^= internal;
            block.encrypt(keys);
            internal = block;
        }
        void decrypt(State& block, const State keys[]){
            State new_internal = block;
            block.decrypt(keys);
            block ^= internal;
            internal = new_internal;
        }
    };

    template<int Nk, int Nr, int Nb=4, template<class S, class... K> class Mode=CBC>
    class Rijndael{
        /*
            Nb - number of 32-bit words in state
            Nk - number of 32-bit words in key
            Nr - number of rounds in algorithm
        */
        constexpr static int BLOCK_SIDE = 4;
        constexpr static int BLOCK_LEN  = Nb * BLOCK_SIDE;
        constexpr static int KEY_LEN    = Nk * BLOCK_SIDE;
        using Matrix = std::array<std::array<Poly, Nb>, BLOCK_SIDE>;
        
        struct State{
            Matrix state;

            State(): state{} {}

            template<class Iter>
            State(Iter it){
                for(int j = 0; j < Nb; j++){ // column-wise matrix, so changed order of iterations
                    for(int i = 0; i < BLOCK_SIDE; i++){
                        state[i][j] = *(it++);
                    }
                }
            }

            void sub_bytes(const Poly s_box[256]){
                for(auto& row : state){
                    for(Poly& e : row){
                        e = s_box[int(e)];
                    }
                }
            }

            void shift_rows(bool inv){
                for(int i = 1; i < BLOCK_SIDE; i++){
                    std::rotate(state[i].begin(),
                                state[i].begin()+(!inv ? i : Nb-i), state[i].end());
                }
            }

            void mix_columns(const Poly mat[Nb][Nb]){
                Matrix res;
                for(int i = 0; i < BLOCK_SIDE; i++){
                    for(int j = 0; j < Nb; j++){
                        for(int k = 0; k < Nb; k++){
                            res[i][j] += mat[i][k] * state[k][j];
                        }
                    }
                }
                state = res;
            }

            State& operator^=(const State& x){
                for(int i = 0; i < BLOCK_SIDE; i++){
                    for(int j = 0; j < Nb; j++){
                        state[i][j] += x.state[i][j];
                    }
                }
                return *this;
            }

            void add_round_key(const State& key){
                *this ^= key;
            }

            void copy_to(std::vector<unsigned char>::iterator it){
                for(int j = 0; j < Nb; j++){ // column-wise matrix, so changed order of iterations
                    for(int i = 0; i < BLOCK_SIDE; i++){
                        *(it++) = (unsigned char)state[i][j];
                    }
                }
            }
        
            void encrypt(const State round_keys[Nr+1]){
                // Round 0
                add_round_key(round_keys[0]);
                // Round 1...Nr
                for(int r = 1; r <= Nr; r++){
                    sub_bytes(S_BOX);
                    shift_rows(false);
                    if (r != Nr) mix_columns(MIX_COL_MAT);
                    add_round_key(round_keys[r]);
                }
            }

            void decrypt(const State round_keys[Nr+1]){
                //Round Nr
                add_round_key(round_keys[Nr]);
                // Round Nr-1 to 1
                for(int r = Nr-1; r >= 1; r--){
                    shift_rows(true);
                    sub_bytes(INV_S_BOX);
                    add_round_key(round_keys[r]);
                    if(r != Nr) mix_columns(INV_MIX_COL_MAT);
                }
                // Round 0
                shift_rows(true);
                sub_bytes(INV_S_BOX);
                add_round_key(round_keys[0]);
            }
        };
        
        State round_keys[Nr+1];
        std::array<unsigned char, BLOCK_LEN> iv;

        void key_expansion(const std::array<unsigned char, KEY_LEN>& in_key){
            std::array<Poly, (Nr + 1) * BLOCK_LEN> w;
            // Copy main key
            for(int i = 0; i < KEY_LEN; i++){
                w[i] = in_key[i];
            }

            Poly round_coef(1);
            for(int i = KEY_LEN; i < (int)w.size(); i += BLOCK_SIDE){
                std::array<Poly, BLOCK_SIDE> add;
                for(int j = 0; j < BLOCK_SIDE; j++){
                    add[j] = w[i + j - BLOCK_SIDE];
                }

                if (i % KEY_LEN == 0){
                    // g-function
                    std::rotate(add.begin(), add.begin()+1, add.end());
                    for(int j = 0; j < 4; j++){
                        add[j] = S_BOX[(int)add[j]];
                    }
                    add[0] += round_coef;
                    round_coef *= Poly(2); // multiply by x
                }else if (Nk > 6 && i % KEY_LEN == 16){
                    // h-function
                    for(int j = 0; j < BLOCK_SIDE; j++){
                        add[j] = S_BOX[(int)add[j]];
                    }
                }

                for(int j = 0; j < BLOCK_SIDE; j++){
                    w[i + j] = w[i + j - KEY_LEN] + add[j];
                }
            }
            for(int k = 0; k <= Nr; k++){
                round_keys[k] = State(w.begin() + k*BLOCK_LEN);
            }
        }

    public:
        Rijndael(const std::array<unsigned char, KEY_LEN>& in_key, const std::array<unsigned char, BLOCK_LEN>& iv_init={}){
            static_assert(Nk == 4 || Nk == 6 || Nk == 8);
            key_expansion(in_key);
            iv = iv_init;
        }

        std::vector<unsigned char> encrypt(const std::vector<unsigned char>& data){
            // Always add padding to the plaintext
            // Padding scheme - PKCS#7: add n bytes of value n
            const size_t res_len = (data.size()/BLOCK_LEN + 1) * BLOCK_LEN; 
            std::vector<unsigned char> res(res_len, res_len - data.size());
            std::copy(data.begin(), data.end(), res.begin());

            Mode<State> enc_mode(iv.begin());

            for(auto it = res.begin(); it != res.end(); it += BLOCK_LEN){
                State state(it);
                enc_mode.encrypt(state, round_keys);
                state.copy_to(it);
            }
            return res;
        }
        
        std::vector<unsigned char> decrypt(const std::vector<unsigned char>& data){
            const size_t n_block = (data.size() + BLOCK_LEN - 1) / BLOCK_LEN; // ceil division
            std::vector<unsigned char> res(n_block * BLOCK_LEN, 0);
            std::copy(data.begin(), data.end(), res.begin());
            
            Mode<State> dec_mode(iv.begin());

            for(auto it = res.begin(); it != res.end(); it += BLOCK_LEN){
                State state(it);
                dec_mode.decrypt(state, round_keys);
                state.copy_to(it);
            }
            // As we use PKCS#7, we know lenght of padding - value of last byte
            res.resize(res.size() - res.back());
            return res;
        }
    };

    using AES128 = Rijndael<4, 10>;
    using AES192 = Rijndael<6, 12>;
    using AES256 = Rijndael<8, 14>;
} // namespace AES
