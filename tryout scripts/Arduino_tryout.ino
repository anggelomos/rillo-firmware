
byte toggle_pins[11][2] = {{2,0}, {3,0}, {4,0}, {5,0}, {6,0}, {7,0}, {8,0}, {9,0}, {10,0}, {11,0}, {12,0}};
String input = "idle";
bool estado_actual;

void setup() {
  // put your setup code here, to run once:
  
  for(int pin = 0; pin <= 11; pin++){
        pinMode(toggle_pins[pin][0], OUTPUT);
        digitalWrite(toggle_pins[pin][0], LOW);
      }
  
  Serial.begin(9600);
  Serial.setTimeout(100);
}

void loop() {
  // put your main code here, to run repeatedly:

   if(Serial.available()>0){        // lee el puerto serial y almacena en estado
      input = Serial.readString();
    }
  
    input.trim(); //Limpia la entrada del puerto serial

    if(isDigit(input[0])){
      toggle_pins[input.toInt()][1] = !(toggle_pins[input.toInt()][1]);
      Serial.print(String(toggle_pins[input.toInt()][0] - 2));
      Serial.print(" - ");
      Serial.println(String(toggle_pins[input.toInt()][1]));
      digitalWrite(toggle_pins[input.toInt()][0], toggle_pins[input.toInt()][1]);
      //estado_actual = toggle_pins[input][1];
      
      input = "idle";
    }
}
