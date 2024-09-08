#define DLL_EXPORT __declspec(dllexport)   
#define WIN32_LEAN_AND_MEAN

#include <windows.h>

#include "../AES.cpp"

extern "C" {
    AES::AES128* DLL_EXPORT WINAPI AES128_new(unsigned char *key_data) {
        std::array<unsigned char, 16> key;
        for(int i = 0; i < 16; i++) key[i] = key_data[i];
        auto x = new AES::AES128(key);
        return x;
    }

    void DLL_EXPORT WINAPI AES128_encrypt(AES::AES128* self, char *data, size_t len, char *res){
        std::vector<unsigned char> text(data, data + len);
        std::vector<unsigned char> chifertext = self->encrypt(text);
        std::copy(chifertext.begin(), chifertext.end(), res);
    }
    
    void DLL_EXPORT WINAPI AES128_decrypt(AES::AES128* self, char *data, size_t len, char *res){
        std::vector<unsigned char> chifertext(data, data + len);
        std::vector<unsigned char> text = self->decrypt(chifertext);
        std::copy(text.begin(), text.end(), res);
    }

    void DLL_EXPORT WINAPI AES128_delete(AES::AES128* self){
        delete self;
    }
}