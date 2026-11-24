#include <Servo.h>

#define ABIERTO 180
#define CERRADO 0

Servo pulgar;
Servo menique;
Servo anular;
Servo medio;
Servo indice;

void setup() {

  Serial.begin(9600);

  pulgar.attach(2);   // PIN 2
  menique.attach(3);  // PIN 3
  anular.attach(4);   // PIN 4
  medio.attach(5);    // PIN 5
  indice.attach(6);   // PIN 6

  pulgar.write(ABIERTO);
  menique.write(ABIERTO);
  anular.write(ABIERTO);
  medio.write(ABIERTO);
  indice.write(ABIERTO);
}

void loop() {

  if (Serial.available()) {

    char comando = Serial.read();

    switch (comando) {

      // ÍNDICE
      case '1':
        indice.write(CERRADO);
        break;

      case 'A':
        indice.write(ABIERTO);
        break;

      // MEDIO
      case '2':
        medio.write(CERRADO);
        break;

      case 'B':
        medio.write(ABIERTO);
        break;

      // ANULAR
      case '3':
        anular.write(CERRADO);
        break;

      case 'C':
        anular.write(ABIERTO);
        break;

      // MEÑIQUE
      case '4':
        menique.write(CERRADO);
        break;

      case 'D':
        menique.write(ABIERTO);
        break;

      // PULGAR
      case '5':
        pulgar.write(CERRADO);
        break;

      case 'E':
        pulgar.write(ABIERTO);
        break;
    }
  }
}