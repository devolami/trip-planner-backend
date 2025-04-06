def auto_fill_logbook(
    duration_from_current_location_to_pickup: float,
    total_time_minutes: float,
    total_distance_miles: float,
    previous_total_time_traveled: float = 0,
    prev_sleeper_berth_hr: float = 0,
    prev_miles_traveled: float = 0,
    has_arrived_at_pickup: bool = False,
):
    """
    Simulates and generates a driver's logbook based on given parameters.

    Args:
        current_cycle_hours: Hours already used in the current cycle.
        duration_from_current_location_to_pickup: Duration in minutes to reach pickup.
        total_time_minutes: Total driving time in minutes.
        total_distance_miles: Total distance in miles.
        previous_total_time_traveled: Total time traveled from previous days.
        prev_sleeper_berth_hr: Hours spent in sleeper berth from the previous day.

    Returns:
        A list of logbooks, where each logbook represents a day.
    """

    driving_time = total_time_minutes
    miles_traveled = prev_miles_traveled  # Track distance driven
    time_traveled_within_eight_hrs = 0
    current_on_duty_hour = 0

    time_spent_in_off_duty = 0
    time_spent_in_on_duty = 0
    time_spent_in_driving = 0
    time_spent_in_sleeper_berth = 0

    LOG_HALF_MINUTE = 0.5
    MAX_SLEEPER_BERTH = 10
    MAX_DRIVING_WITHIN_EIGHT_HRS = 7.5 * 60
    MAX_DRIVING_TIME = 10.5
    MAX_MILES_BEFORE_REFUELING = 980
    MAX_ON_DUTY_TIME = 13.5
    RESUMPTION_TIME = 6.5

    logbooks = []
    total_time_traveled = previous_total_time_traveled
    current_hour = 0

    def generate_new_log():
        return {
            "logbook": [],
            "currentHour": 0,
            "totalTimeTraveled": total_time_traveled,
            "timeSpentInOffDuty": time_spent_in_off_duty,
            "timeSpentInOnDuty": time_spent_in_on_duty,
            "timeSpentInDriving": time_spent_in_driving,
            "timeSpentInSleeperBerth": time_spent_in_sleeper_berth,
        }

    new_log = generate_new_log()
    logbooks.append(new_log)

    if prev_sleeper_berth_hr >= MAX_SLEEPER_BERTH:
        # Step 1: Start at On-Duty (Vehicle Check)

        current_hour, current_on_duty_hour, time_spent_in_on_duty = switch_to_on_duty(
            new_log,
            current_hour,
            current_on_duty_hour,
            time_spent_in_on_duty,
            action="Pre-trip/TIV",
        )

        # Step 3: Start Driving to Pickup or drop-off
        (
            current_hour,
            current_on_duty_hour,
            time_spent_in_driving,
            total_time_traveled,
            time_traveled_within_eight_hrs,
            miles_traveled,
        ) = start_driving(
            new_log,
            current_hour,
            current_on_duty_hour,
            time_spent_in_driving,
            total_time_traveled,
            time_traveled_within_eight_hrs,
            miles_traveled,
            total_distance_miles,
            driving_time,
        )

    elif 0 < prev_sleeper_berth_hr < MAX_SLEEPER_BERTH:

        # Step 1: Start at sleeper berth until you have spent 10 hours there
        sleeper_time = MAX_SLEEPER_BERTH - prev_sleeper_berth_hr
        current_hour, current_on_duty_hour, time_spent_in_sleeper_berth = (
            switch_to_sleeper_berth(
                new_log,
                current_hour,
                current_on_duty_hour,
                time_spent_in_sleeper_berth,
                rate=sleeper_time,
            )
        )
        # Step 2: Switch to On-Duty (Vehicle Check)
        current_hour, current_on_duty_hour, time_spent_in_on_duty = switch_to_on_duty(
            new_log,
            current_hour,
            current_on_duty_hour,
            time_spent_in_on_duty,
            action="Pre-trip/TIV",
        )

        # Step 4: Start Driving to Pickup or drop-off
        (
            current_hour,
            current_on_duty_hour,
            time_spent_in_driving,
            total_time_traveled,
            time_traveled_within_eight_hrs,
            miles_traveled,
        ) = start_driving(
            new_log,
            current_hour,
            current_on_duty_hour,
            time_spent_in_driving,
            total_time_traveled,
            time_traveled_within_eight_hrs,
            miles_traveled,
            total_distance_miles,
            driving_time,
        )
    else:

        current_hour, time_spent_in_off_duty = switch_to_off_duty(
            new_log,
            current_hour,
            time_spent_in_off_duty,
            rate=RESUMPTION_TIME,
            action=None,
        )

        # Step 2: Switch to On-Duty (Vehicle Check)
        current_hour, current_on_duty_hour, time_spent_in_on_duty = switch_to_on_duty(
            new_log,
            current_hour,
            current_on_duty_hour,
            time_spent_in_on_duty,
            action="Pre-trip/TIV",
        )
        # Step 4: Start Driving to Pickup
        (
            current_hour,
            current_on_duty_hour,
            time_spent_in_driving,
            total_time_traveled,
            time_traveled_within_eight_hrs,
            miles_traveled,
        ) = start_driving(
            new_log,
            current_hour,
            current_on_duty_hour,
            time_spent_in_driving,
            total_time_traveled,
            time_traveled_within_eight_hrs,
            miles_traveled,
            total_distance_miles,
            driving_time,
        )

    while (
        total_time_traveled < duration_from_current_location_to_pickup
        and not has_arrived_at_pickup
    ):
        # Base Condition: Stop Recursion if pickup location is reached.
        if total_time_traveled >= duration_from_current_location_to_pickup:
            break
        (
            current_hour,
            current_on_duty_hour,
            total_time_traveled,
            time_traveled_within_eight_hrs,
            time_spent_in_driving,
            miles_traveled,
        ) = drive(
            new_log,
            current_hour,
            current_on_duty_hour,
            total_time_traveled,
            time_traveled_within_eight_hrs,
            time_spent_in_driving,
            miles_traveled,
            total_distance_miles,
            driving_time,
        )

        # Mandatory 30-min break after at least every 8 hours of driving
        if time_traveled_within_eight_hrs >= MAX_DRIVING_WITHIN_EIGHT_HRS:

            current_hour, time_spent_in_off_duty = switch_to_off_duty(
                new_log,
                current_hour,
                time_spent_in_off_duty,
                rate=LOG_HALF_MINUTE,
                action="30-minute break",
            )

            (
                current_hour,
                current_on_duty_hour,
                time_spent_in_driving,
                total_time_traveled,
                time_traveled_within_eight_hrs,
                miles_traveled,
            ) = start_driving(
                new_log,
                current_hour,
                current_on_duty_hour,
                time_spent_in_driving,
                total_time_traveled,
                time_traveled_within_eight_hrs,
                miles_traveled,
                total_distance_miles,
                driving_time,
            )
            time_traveled_within_eight_hrs = 0

        # Refuelling
        if miles_traveled >= MAX_MILES_BEFORE_REFUELING:
            current_hour, current_on_duty_hour, time_spent_in_on_duty = (
                switch_to_on_duty(
                    new_log,
                    current_hour,
                    current_on_duty_hour,
                    time_spent_in_on_duty,
                    action="Refueling",
                )
            )
            miles_traveled = 0
            time_traveled_within_eight_hrs = 0
            (
                current_hour,
                current_on_duty_hour,
                time_spent_in_driving,
                total_time_traveled,
                time_traveled_within_eight_hrs,
                miles_traveled,
            ) = start_driving(
                new_log,
                current_hour,
                current_on_duty_hour,
                time_spent_in_driving,
                total_time_traveled,
                time_traveled_within_eight_hrs,
                miles_traveled,
                total_distance_miles,
                driving_time,
            )

        if (
            time_spent_in_driving >= MAX_DRIVING_TIME
            or current_on_duty_hour >= MAX_ON_DUTY_TIME
        ):
            sleeper_time = 24 - current_hour

            (
                current_hour,
                current_on_duty_hour,
                time_spent_in_sleeper_berth,
            ) = switch_to_sleeper_berth(
                new_log,
                current_hour,
                current_on_duty_hour,
                time_spent_in_sleeper_berth,
                rate=sleeper_time,
            )

            new_log["timeSpentInOffDuty"] = time_spent_in_off_duty
            new_log["timeSpentInOnDuty"] = time_spent_in_on_duty
            new_log["timeSpentInDriving"] = time_spent_in_driving
            new_log["timeSpentInSleeperBerth"] = time_spent_in_sleeper_berth

            next_day_logs = auto_fill_logbook(
                duration_from_current_location_to_pickup
                - total_time_traveled,  # Remaining travel time to pickup
                total_time_minutes,  # Remaining total trip time
                total_distance_miles,
                total_time_traveled,  # Keep tracking time across days
                sleeper_time,
                miles_traveled,
                has_arrived_at_pickup=False,
            )

            return logbooks + next_day_logs  # Combine all logbooks

        # Step 5: Arrive at Pickup, Stay On-Duty for 30 minutes
    if not has_arrived_at_pickup:
        current_hour, current_on_duty_hour, time_spent_in_on_duty = switch_to_on_duty(
            new_log,
            current_hour,
            current_on_duty_hour,
            time_spent_in_on_duty,
            action="Pickup",
        )
        has_arrived_at_pickup = True
        time_traveled_within_eight_hrs = 0

        # Step 6: Start Driving to Drop-off Immediately
        (
            current_hour,
            current_on_duty_hour,
            time_spent_in_driving,
            total_time_traveled,
            time_traveled_within_eight_hrs,
            miles_traveled,
        ) = start_driving(
            new_log,
            current_hour,
            current_on_duty_hour,
            time_spent_in_driving,
            total_time_traveled,
            time_traveled_within_eight_hrs,
            miles_traveled,
            total_distance_miles,
            driving_time,
        )

    # Step 7: Continue Driving to Drop-off
    while total_time_traveled < driving_time:
        # Base Condition: Stop Recursion if Trip is Done
        if total_time_traveled >= driving_time:
            break  # Trip is complete, return logs
        (
            current_hour,
            current_on_duty_hour,
            total_time_traveled,
            time_traveled_within_eight_hrs,
            time_spent_in_driving,
            miles_traveled,
        ) = drive(
            new_log,
            current_hour,
            current_on_duty_hour,
            total_time_traveled,
            time_traveled_within_eight_hrs,
            time_spent_in_driving,
            miles_traveled,
            total_distance_miles,
            driving_time,
        )

        # Mandatory 30-min break after at least every 8 hours of driving
        if time_traveled_within_eight_hrs >= MAX_DRIVING_WITHIN_EIGHT_HRS:
            current_hour, time_spent_in_off_duty = switch_to_off_duty(
                new_log,
                current_hour,
                time_spent_in_off_duty,
                rate=LOG_HALF_MINUTE,
                action="30-minute break",
            )

            (
                current_hour,
                current_on_duty_hour,
                time_spent_in_driving,
                total_time_traveled,
                time_traveled_within_eight_hrs,
                miles_traveled,
            ) = start_driving(
                new_log,
                current_hour,
                current_on_duty_hour,
                time_spent_in_driving,
                total_time_traveled,
                time_traveled_within_eight_hrs,
                miles_traveled,
                total_distance_miles,
                driving_time,
            )
            time_traveled_within_eight_hrs = 0

        # Refuelling
        if miles_traveled >= MAX_MILES_BEFORE_REFUELING:
            current_hour, current_on_duty_hour, time_spent_in_on_duty = (
                switch_to_on_duty(
                    new_log,
                    current_hour,
                    current_on_duty_hour,
                    time_spent_in_on_duty,
                    action="Refueling",
                )
            )
            miles_traveled = 0
            time_traveled_within_eight_hrs = 0
            (
                current_hour,
                current_on_duty_hour,
                time_spent_in_driving,
                total_time_traveled,
                time_traveled_within_eight_hrs,
                miles_traveled,
            ) = start_driving(
                new_log,
                current_hour,
                current_on_duty_hour,
                time_spent_in_driving,
                total_time_traveled,
                time_traveled_within_eight_hrs,
                miles_traveled,
                total_distance_miles,
                driving_time,
            )

        # Stop Driving at least every 11 total hours of driving or 14 hours of on-duty (Switch to Sleeper Berth)
        if (
            time_spent_in_driving >= MAX_DRIVING_TIME
            or current_on_duty_hour >= MAX_ON_DUTY_TIME
        ):
            sleeper_time = 24 - current_hour

            (
                current_hour,
                current_on_duty_hour,
                time_spent_in_sleeper_berth,
            ) = switch_to_sleeper_berth(
                new_log,
                current_hour,
                current_on_duty_hour,
                time_spent_in_sleeper_berth,
                rate=sleeper_time,
            )

            new_log["timeSpentInOffDuty"] = time_spent_in_off_duty
            new_log["timeSpentInOnDuty"] = time_spent_in_on_duty
            new_log["timeSpentInDriving"] = time_spent_in_driving
            new_log["timeSpentInSleeperBerth"] = time_spent_in_sleeper_berth

            # Start a New Day & Continue Logging (Recursive Call)
            next_day_logs = auto_fill_logbook(
                driving_time - total_time_traveled,  # Remaining travel time to pickup
                total_time_minutes,  # Remaining total trip time
                total_distance_miles,
                total_time_traveled,  # Keep tracking time across days
                sleeper_time,
                miles_traveled,
                has_arrived_at_pickup,
            )

            return logbooks + next_day_logs  # Combine all logbooks

    # Step 8: On-Duty at Drop-off before Sleeping
    current_hour, current_on_duty_hour, time_spent_in_on_duty = switch_to_on_duty(
        new_log,
        current_hour,
        current_on_duty_hour,
        time_spent_in_on_duty,
        action="Drop-off",
    )
    time_traveled_within_eight_hrs = 0

    # Step 9: Switch to off-duty (End of the Trip)
    remaining_hour = 24 - current_hour
    current_hour, time_spent_in_off_duty = switch_to_off_duty(
        new_log,
        current_hour,
        time_spent_in_off_duty,
        rate=remaining_hour,
        action=None,
    )

    new_log["timeSpentInOffDuty"] = time_spent_in_off_duty
    new_log["timeSpentInOnDuty"] = time_spent_in_on_duty
    new_log["timeSpentInDriving"] = time_spent_in_driving
    new_log["timeSpentInSleeperBerth"] = time_spent_in_sleeper_berth

    return logbooks  # Return multiple days of logs


# ===================================== HELPER FUNCTIONS =======================================================

LOG_HALF_MINUTE = 0.5
HALF_MINUTE = 30  # In minutes.


def switch_to_on_duty(
    log, current_hour, current_on_duty_hour, time_spent_in_on_duty, action
):
    log["logbook"].append({"hour": current_hour, "row": "on-duty"})
    current_hour += LOG_HALF_MINUTE
    current_on_duty_hour += LOG_HALF_MINUTE
    time_spent_in_on_duty += LOG_HALF_MINUTE
    log["logbook"].append({"hour": current_hour, "row": "on-duty", "action": action})
    return current_hour, current_on_duty_hour, time_spent_in_on_duty


def switch_to_off_duty(log, current_hour, time_spent_in_off_duty, rate, action):
    log["logbook"].append({"hour": current_hour, "row": "off-duty"})
    current_hour += rate
    time_spent_in_off_duty += rate

    log["logbook"].append({"hour": current_hour, "row": "off-duty", "action": action})
    return current_hour, time_spent_in_off_duty


def switch_to_sleeper_berth(
    log,
    current_hour,
    current_on_duty_hour,
    time_spent_in_sleeper_berth,
    rate,
):
    log["logbook"].append({"hour": current_hour, "row": "sleeper"})
    current_hour += rate
    time_spent_in_sleeper_berth += rate
    current_on_duty_hour = 0

    log["logbook"].append({"hour": current_hour, "row": "sleeper"})
    return (
        current_hour,
        current_on_duty_hour,
        time_spent_in_sleeper_berth,
    )


def start_driving(
    log,
    current_hour,
    current_on_duty_hour,
    time_spent_in_driving,
    total_time_traveled,
    time_traveled_within_eight_hrs,
    miles_traveled,
    total_distance_miles,
    driving_time,
):
    log["logbook"].append({"hour": current_hour, "row": "driving"})
    current_hour += LOG_HALF_MINUTE
    current_on_duty_hour += LOG_HALF_MINUTE
    time_spent_in_driving += LOG_HALF_MINUTE
    total_time_traveled += LOG_HALF_MINUTE
    time_traveled_within_eight_hrs += HALF_MINUTE
    miles_traveled += (
        total_distance_miles / driving_time
    ) * HALF_MINUTE  # Convert minutes to miles

    log["logbook"].append({"hour": current_hour, "row": "driving"})
    return (
        current_hour,
        current_on_duty_hour,
        time_spent_in_driving,
        total_time_traveled,
        time_traveled_within_eight_hrs,
        miles_traveled,
    )


def drive(
    log,
    current_hour,
    current_on_duty_hour,
    total_time_traveled,
    time_traveled_within_eight_hrs,
    time_spent_in_driving,
    miles_traveled,
    total_distance_miles,
    driving_time,
):
    current_hour += LOG_HALF_MINUTE
    current_on_duty_hour += LOG_HALF_MINUTE
    total_time_traveled += HALF_MINUTE
    time_traveled_within_eight_hrs += HALF_MINUTE
    time_spent_in_driving += LOG_HALF_MINUTE
    miles_traveled += (
        total_distance_miles / driving_time
    ) * HALF_MINUTE  # Convert minutes to miles

    log["logbook"].append({"hour": current_hour, "row": "driving"})
    return (
        current_hour,
        current_on_duty_hour,
        total_time_traveled,
        time_traveled_within_eight_hrs,
        time_spent_in_driving,
        miles_traveled,
    )
