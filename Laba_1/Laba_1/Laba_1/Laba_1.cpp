#include <iostream>
#include <string>
#include <conio.h>
#include <windows.h>

char bufRus[256];
char* Rus(const char* text) {
    CharToOemA(text, bufRus);
    return bufRus;
}

using namespace std;

class InternetOperator
{
public:

    InternetOperator() : imya("Name"), abonent(0), cena(0) {};
    InternetOperator(string n, int c, double p) {
        imya = n;
        if (c < 0)
            abonent = 0;
        else
            abonent = c;
        if (p < 0)
            cena = 0;
        else
            cena = p;
    };
    double getItog() {
        return cena * abonent;
    }

    string getImya() {
        return imya;
    }

    void setAbonent(int count) {
        if (count < 0)
            abonent = 0;
        else
            abonent = count;
    }

    void setPrice(double p) {
        if (p < 0)
            cena = 0;
        else
            cena = p;

    }

private:
    string imya;
    double cena;
    int abonent;
};

int main() {
    InternetOperator Rostelecom(Rus("Ростелеком"), 45216, 1990.90);
    printf(Rus("Выручка компании %s: %f"), Rostelecom.getImya().c_str(), Rostelecom.getItog());
    return 0;
}