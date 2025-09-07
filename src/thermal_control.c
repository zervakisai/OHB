#include <stdio.h>
#include <stdlib.h>
#include <math.h>

// Temperature operating limits
#define MIN_TEMP -20.0f
#define MAX_TEMP 50.0f

// Control thresholds
#define HEATER_ON_THRESHOLD 0.0f
#define HEATER_OFF_THRESHOLD 40.0f

// Safety thresholds
#define CRITICAL_LOW -15.0f
#define CRITICAL_HIGH 45.0f

int control_heater(float current_temp, int prev_state, float dt) {
    // Invalid timestep
    if (dt <= 0.0f) {
        return -1; // INVALID_INPUT
    }

    // Sensor error
    if (fabs(current_temp - 999.0f) < 1e-6) {
        return -1; // INVALID_INPUT
    }

    // Safety shutdown if critical limits exceeded
    if (current_temp < CRITICAL_LOW || current_temp > CRITICAL_HIGH) {
        return -2; // SAFETY_MODE
    }

    // Control logic
    if (current_temp < HEATER_ON_THRESHOLD) {
        return 1; // Turn ON heater
    }
    if (current_temp > HEATER_OFF_THRESHOLD) {
        return 0; // Turn OFF heater
    }

    // Within limits: maintain previous state
    return prev_state;
}

int main(int argc, char *argv[]) {
    if (argc != 4) {
        printf("Usage: %s <current_temp> <prev_state> <dt>\n", argv[0]);
        return 1;
    }

    float current_temp = atof(argv[1]);
    int prev_state = atoi(argv[2]);
    float dt = atof(argv[3]);

    int heater_cmd = control_heater(current_temp, prev_state, dt);
    printf("%d\n", heater_cmd);
    return 0;
}