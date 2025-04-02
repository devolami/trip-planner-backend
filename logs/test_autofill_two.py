def auto_fill_logbook(
    duration_from_current_location_to_pickup: float,
    total_time_minutes: float,
    total_distance_miles: float,
    previous_total_time_traveled: float = 0,
    prev_sleeper_berth_hr: float = 0,
    prev_miles_traveled: float = 0,
    prev_has_arrived_at_pickup: bool = False,
):
    """
    Simulates and generates a driver's logbook based on given parameters.

    Args:
        duration_from_current_location_to_pickup: Duration in minutes to reach pickup.
        total_time_minutes: Total driving time in minutes.
        total_distance_miles: Total distance in miles.
        previous_total_time_traveled: Total time traveled from previous days.
        prev_sleeper_berth_hr: Hours spent in sleeper berth from the previous day.

    Returns:
        A list of logbooks, where each logbook represents a day.
    """

    # Initialize variables
    miles_traveled = prev_miles_traveled
    total_time_traveled = previous_total_time_traveled
    current_hour = 0
    current_on_duty_hour = 0
    time_traveled_within_eight_hrs = 0
    time_spent = {"off_duty": 0, "on_duty": 0, "driving": 0, "sleeper": 0}
    has_arrived_at_pickup = prev_has_arrived_at_pickup

    logbooks = []
    new_log = generate_new_log(total_time_traveled, time_spent)
    logbooks.append(new_log)

    # Handle rest and transition to on-duty
    current_hour, current_on_duty_hour, total_time_traveled = handle_day_initial_duty(
        new_log,
        prev_sleeper_berth_hr,
        current_hour,
        time_spent,
        total_time_traveled,
        current_on_duty_hour,
    )

    # Start driving towards pickup or drop-off
    current_hour = start_driving(new_log, current_hour, time_spent)

    # Continue driving towards pickup
    while (
        total_time_traveled < duration_from_current_location_to_pickup
        and not has_arrived_at_pickup
    ):
        if total_time_traveled >= duration_from_current_location_to_pickup:
            break
        (
            current_hour,
            miles_traveled,
            total_time_traveled,
            miles_traveled,
            time_traveled_within_eight_hrs,
        ) = drive(
            new_log,
            current_hour,
            total_time_traveled,
            total_distance_miles,
            time_traveled_within_eight_hrs,
            miles_traveled,
            total_time_minutes,
            time_spent,
        )

        # Handle breaks and refueling
        (
            current_hour,
            current_on_duty_hour,
            total_time_traveled,
            time_traveled_within_eight_hrs,
        ) = handle_breaks(
            new_log,
            current_hour,
            time_traveled_within_eight_hrs,
            time_spent,
            current_on_duty_hour,
            total_time_traveled,
        )
        (
            current_hour,
            current_on_duty_hour,
            time_traveled_within_eight_hrs,
            miles_traveled,
            total_time_traveled,
        ) = handle_refueling(
            new_log,
            current_hour,
            miles_traveled,
            time_spent,
            time_traveled_within_eight_hrs,
            total_time_traveled,
        )
        logbooks, new_log, current_hour = handle_driving_and_on_duty_limits(
            new_log,
            time_spent,
            current_on_duty_hour,
            current_hour,
            duration_from_current_location_to_pickup - total_time_traveled,
            total_time_minutes,
            total_distance_miles,
            total_time_traveled,
            miles_traveled,
            prev_has_arrived_at_pickup=False,
            logbooks=logbooks,
        )

    # Arriving at Pickup
    if not has_arrived_at_pickup:
        current_hour, current_on_duty_hour, total_time_traveled = arrive_at_location(
            new_log,
            current_hour,
            time_spent,
            current_on_duty_hour,
            total_time_traveled,
            action="Pickup",
        )
        has_arrived_at_pickup = True

    # Start Driving to Drop-off
    while total_time_traveled < total_time_minutes:
        if total_time_traveled >= total_time_minutes:
            break  # Trip is complete, return logs
        (
            current_hour,
            miles_traveled,
            total_time_traveled,
            miles_traveled,
            time_traveled_within_eight_hrs,
        ) = drive(
            new_log,
            current_hour,
            total_time_traveled,
            total_distance_miles,
            time_traveled_within_eight_hrs,
            miles_traveled,
            total_time_minutes,
            time_spent,
        )

        (
            current_hour,
            current_on_duty_hour,
            total_time_traveled,
            time_traveled_within_eight_hrs,
        ) = handle_breaks(
            new_log,
            current_hour,
            time_traveled_within_eight_hrs,
            time_spent,
            current_on_duty_hour,
            total_time_traveled,
        )
        (
            current_hour,
            current_on_duty_hour,
            time_traveled_within_eight_hrs,
            miles_traveled,
            total_time_traveled,
        ) = handle_refueling(
            new_log,
            current_hour,
            miles_traveled,
            time_spent,
            time_traveled_within_eight_hrs,
            total_time_traveled,
        )

        logbooks, new_log, current_hour = handle_driving_and_on_duty_limits(
            new_log,
            time_spent,
            current_on_duty_hour,
            current_hour,
            duration_from_current_location_to_pickup - total_time_traveled,
            total_time_minutes,
            total_distance_miles,
            total_time_traveled,
            miles_traveled,
            prev_has_arrived_at_pickup=False,
            logbooks=logbooks,
        )

    # Arriving at Drop-off
    current_hour, current_on_duty_hour, total_time_traveled = arrive_at_location(
        new_log,
        current_hour,
        time_spent,
        current_on_duty_hour,
        total_time_traveled,
        action="Drop-off",
    )

    # End the trip
    current_hour = end_trip(new_log, current_hour, time_spent, logbooks)

    return logbooks


# ========================= HELPER FUNCTIONS =========================


def generate_new_log(total_time_traveled, time_spent):
    """Creates a new log template."""
    return {
        "logbook": [],
        "totalTimeTraveled": total_time_traveled,
        "timeSpent": time_spent.copy(),
    }


def handle_day_initial_duty(
    log,
    prev_sleeper_berth_hr,
    current_hour,
    time_spent,
    total_time_traveled,
    current_on_duty_hour,
):
    MAX_SLEEPER_BERTH_TIME = 10
    FIRST_DAY_RESUMPTION_TIME = 6.5
    if prev_sleeper_berth_hr >= MAX_SLEEPER_BERTH_TIME:
        current_hour = switch_to_on_duty(
            log, current_hour, time_spent, action="Pre-trip/TIV"
        )
        current_hour, current_on_duty_hour, total_time_traveled = start_driving(
            log, current_hour, time_spent, current_on_duty_hour, total_time_traveled
        )

    elif 0 < prev_sleeper_berth_hr < MAX_SLEEPER_BERTH_TIME:
        # Step 1: Start at sleeper berth until you have spent 10 hours there
        log["logbook"].append({"hour": current_hour, "row": "sleeper"})
        current_hour += MAX_SLEEPER_BERTH_TIME - prev_sleeper_berth_hr
        time_spent["sleeper"] += MAX_SLEEPER_BERTH_TIME - prev_sleeper_berth_hr
        log["logbook"].append({"hour": current_hour, "row": "sleeper"})

        current_hour = switch_to_on_duty(
            log, current_hour, time_spent, action="Pre-trip/TIV"
        )
        current_hour, current_on_duty_hour, total_time_traveled = start_driving(
            log, current_hour, time_spent, current_on_duty_hour, total_time_traveled
        )
    else:
        log["logbook"].append({"hour": current_hour, "row": "off-duty"})
        current_hour += FIRST_DAY_RESUMPTION_TIME
        time_spent["off-duty"] += FIRST_DAY_RESUMPTION_TIME
        log["logbook"].append({"hour": current_hour, "row": "off-duty"})
        current_hour = switch_to_on_duty(
            log, current_hour, time_spent, action="Pre-trip/TIV"
        )
        current_hour, current_on_duty_hour, total_time_traveled = start_driving(
            log, current_hour, time_spent, current_on_duty_hour, total_time_traveled
        )

    return current_hour, current_on_duty_hour, total_time_traveled


def switch_to_on_duty(log, current_hour, time_spent, action):
    """Switches the log to on-duty mode and optionally starts driving."""
    log["logbook"].append({"hour": current_hour, "row": "on-duty", "action": action})
    current_hour += 0.5
    time_spent["on-duty"] += 0.5

    return current_hour


def start_driving(
    log, current_hour, time_spent, current_on_duty_hour, total_time_traveled
):
    """Handles the transition from on-duty to driving."""
    log["logbook"].append({"hour": current_hour, "row": "driving"})
    current_hour += 0.5
    time_spent["driving"] += 0.5
    total_time_traveled += 0.5
    current_on_duty_hour += 0.5
    log["logbook"].append({"hour": current_hour, "row": "driving"})
    return current_hour, current_on_duty_hour, total_time_traveled


def drive(
    log,
    current_hour,
    total_time_traveled,
    total_distance_miles,
    time_traveled_within_eight_hrs,
    miles_traveled,
    total_time_minutes,
    time_spent,
):
    """Simulates driving in 30-minute increments."""
    log["logbook"].append({"hour": current_hour, "row": "driving"})
    current_hour += 0.5
    total_time_traveled += 30
    time_traveled_within_eight_hrs += 30
    time_spent["driving"] += 0.5
    miles_traveled += (total_distance_miles / total_time_minutes) * 30
    return (
        current_hour,
        miles_traveled,
        total_time_traveled,
        miles_traveled,
        time_traveled_within_eight_hrs,
    )


def handle_breaks(
    log,
    current_hour,
    time_traveled_within_eight_hrs,
    time_spent,
    current_on_duty_hour,
    total_time_traveled,
):
    """Handles mandatory 30-minute breaks after 8 hours of driving."""
    MAX_CUMULATIVE_DRIVING_TIME = 7 * 60
    if time_traveled_within_eight_hrs >= MAX_CUMULATIVE_DRIVING_TIME:
        log["logbook"].append({"hour": current_hour, "row": "off-duty"})
        current_hour += 0.5
        time_spent["off_duty"] += 0.5
        time_traveled_within_eight_hrs = 0
        log["logbook"].append(
            {"hour": current_hour, "row": "off-duty", "action": "30-minute break"}
        )
        current_hour, current_on_duty_hour, total_time_traveled = start_driving(
            log, current_hour, current_on_duty_hour, time_spent, total_time_traveled
        )
        return (
            current_hour,
            current_on_duty_hour,
            total_time_traveled,
            time_traveled_within_eight_hrs,
        )


def handle_refueling(
    log,
    current_hour,
    miles_traveled,
    time_spent,
    current_on_duty_hour,
    time_traveled_within_eight_hrs,
    total_time_traveled,
):
    """Handles refueling stops."""
    MAX_MILES_BEFORE_REFUEL = 950  # In miles
    if miles_traveled >= MAX_MILES_BEFORE_REFUEL:
        log["logbook"].append({"hour": current_hour, "row": "on-duty"})
        current_hour += 0.5
        current_on_duty_hour += 0.5
        time_spent["on_duty"] += 0.5
        miles_traveled = 0
        time_traveled_within_eight_hrs = 0
        log["logbook"].append(
            {"hour": current_hour, "row": "on-duty", "action": "Refuelling"}
        )
        current_hour, current_on_duty_hour, total_time_traveled = start_driving(
            log, current_hour, current_on_duty_hour, time_spent, total_time_traveled
        )
        return (
            current_hour,
            current_on_duty_hour,
            time_traveled_within_eight_hrs,
            miles_traveled,
            total_time_traveled,
        )


def handle_driving_and_on_duty_limits(
    log,
    time_spent,
    current_on_duty_hour,
    current_hour,
    duration,
    total_time_minutes,
    total_distance_miles,
    total_time_traveled,
    miles,
    prev_has_arrived_at_pickup,
    logbooks,
):
    # Define Legal constants
    MAX_DRIVING_HOURS = 10.5
    MAX_ON_DUTY_HOURS = 13.5
    if (
        time_spent["driving"] >= MAX_DRIVING_HOURS
        or current_on_duty_hour >= MAX_ON_DUTY_HOURS
    ):
        log["logbook"].append({"hour": current_hour, "row": "sleeper"})
        time_to_stay_in_sleeper_berth = 24 - current_hour
        current_hour += time_to_stay_in_sleeper_berth
        time_spent["sleeper"] += time_to_stay_in_sleeper_berth
        log["logbook"].append({"hour": current_hour, "row": "sleeper"})
        new_log = start_new_day(
            duration,
            total_time_minutes,
            total_distance_miles,
            total_time_traveled,
            miles,
            time_spent["sleeper"],
            prev_has_arrived_at_pickup,
        )
        return logbooks, new_log, current_hour


def start_new_day(
    duration,
    total_time_minutes,
    total_distance_miles,
    total_time_traveled,
    miles,
    sleeper,
    prev_has_arrived_at_pickup,
):
    """Starts a new day of logging."""
    return auto_fill_logbook(
        duration - total_time_traveled,
        total_time_minutes,
        total_distance_miles,
        total_time_traveled,
        sleeper,
        miles,
        prev_has_arrived_at_pickup,
    )


def arrive_at_location(
    log, current_hour, time_spent, current_on_duty_hour, total_time_traveled, action
):
    """Handles arrival at a location."""
    current_hour = switch_to_on_duty(log, current_hour, time_spent, action=action)
    current_hour, current_on_duty_hour, total_time_traveled = start_driving(
        log, current_hour, current_on_duty_hour, time_spent, total_time_traveled
    )
    return current_hour, current_on_duty_hour, total_time_traveled


def end_trip(log, current_hour, time_spent):
    """Handles end of the trip and switching to off-duty."""
    log["logbook"].append({"hour": current_hour, "row": "off-duty"})
    remaining_hour = 24 - current_hour
    current_hour += remaining_hour
    time_spent["off-duty"] += remaining_hour
    log["logbook"].append({"hour": current_hour, "row": "off-duty"})

    return current_hour
