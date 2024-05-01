/*
 * HC-SR04 example sketch
 *
 * https://create.arduino.cc/projecthub/Isaac100/getting-started-with-the-hc-sr04-ultrasonic-sensor-036380
 *
 * by Isaac100
 */

const int trigPin = 9;
const int echoPin = 10;
double ema = 0;
const int smoothing_window = 5;
double data[smoothing_window];
int iterations;
int available_spot_ptr = 0;
int timeout = 0;
double current_ema = 0;
const byte numLEDs = 2;
byte ledPin[numLEDs] = {12, 13};
unsigned long LEDinterval[numLEDs] = {200, 400};
unsigned long prevLEDmillis[numLEDs] = {0, 0};
float duration, distance;

void setup() {
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
  Serial.begin(9600);
  //delay(100); 
  // tell the PC we are ready
  Serial.println("<Arduino is ready>");
}

void loop() {
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  duration = pulseIn(echoPin, HIGH);
  //distance = (duration*.0343)/2;
  //current_ema = smoothing_calc(distance);
  Serial.print("<duration: ");
  Serial.print(duration);
  //Serial.print(current_ema);
  Serial.println(">");
  delay(100);
}


double smoothing_calc (double distance) {
  data[available_spot_ptr] = distance;
  available_spot_ptr++;
  double avg = 0;
  if (iterations < 5)
  {
    for(int i = 0; i < available_spot_ptr; i++)
    {
       avg += data[i];
    }
    iterations++;
    avg /= available_spot_ptr;
  }
  else
  {
    for(int i = 0; i < smoothing_window; i++)
    {
       avg += data[i];
    }

    avg /= smoothing_window;
  }

  return avg;

}




/*double ema_calc (double distance) {
  if (ema == 0 && distance < 1200)
  {
    ema = distance;
    timeout  = 0;
  }
  else if (distance < 1200)
  {
      ema = (weight * distance) + ((1 - weight) * ema);
      timeout = 0;
  }
  else
  {
    timeout += 1;
  }
  if (timeout > 6)
  {
    return -1;
  }
  return round(ema);

}*/