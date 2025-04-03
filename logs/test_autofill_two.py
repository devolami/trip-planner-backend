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
    driving_time = total_time_minutes
    miles_traveled = prev_miles_traveled
    total_time_traveled = previous_total_time_traveled
    current_hour = 0
    current_on_duty_hour = 0
    time_traveled_within_eight_hrs = 0
    time_spent = {"off_duty": 0.0, "on_duty": 0.0, "driving": 0.0, "sleeper": 0.0}
    has_arrived_at_pickup = prev_has_arrived_at_pickup

    logbooks = []
    new_log = generate_new_log(total_time_traveled, time_spent)
    logbooks.append(new_log)

    # Handle rest and transition to on_duty
    current_hour, current_on_duty_hour, total_time_traveled = handle_day_initial_duty(
        new_log,
        prev_sleeper_berth_hr,
        current_hour,
        time_spent,
        total_time_traveled,
        current_on_duty_hour,
    )

    # Start driving towards pickup or drop-off
    current_hour, current_on_duty_hour, total_time_traveled = start_driving(
            new_log, current_hour, time_spent, current_on_duty_hour, total_time_traveled
        )

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
            current_on_duty_hour,
            time_traveled_within_eight_hrs,
            total_time_traveled,
        )
        # Handle Maximum 11-hour max driving and 14-hour max on duty time
        current_hour, logbooks = handle_driving_and_on_duty_limits(
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
        # Start driving to Drop-Off
        current_hour, current_on_duty_hour, total_time_traveled = start_driving(
            new_log, current_hour, time_spent, current_on_duty_hour, total_time_traveled
        )

    # Continue Driving to Drop-off
    while total_time_traveled < total_time_minutes:
        if total_time_traveled >= total_time_minutes:
            break  # Trip is complete
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

        # Handle breaks and refuelling

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
            current_on_duty_hour,
            time_traveled_within_eight_hrs,
            total_time_traveled,
        )
        # Handle 11-hour max driving and 14-hour max on duty time

        current_hour, logbooks = handle_driving_and_on_duty_limits(
            new_log,
            time_spent,
            current_on_duty_hour,
            current_hour,
            driving_time - total_time_traveled,
            total_time_minutes,
            total_distance_miles,
            total_time_traveled,
            miles_traveled,
            prev_has_arrived_at_pickup=True,
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
    current_hour = end_trip(new_log, current_hour, time_spent)
    return logbooks


# ========================= HELPER FUNCTIONS =========================


def generate_new_log(total_time_traveled, time_spent):
    """Creates a new log template."""
    return {
        "logbook": [],
        "totalTimeTraveled": total_time_traveled,
        # "timeSpent": time_spent.copy(),
        "timeSpent": time_spent,
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
    if (
        prev_sleeper_berth_hr >= MAX_SLEEPER_BERTH_TIME
    ):  # If driver has spent at least 10 hours in sleeper berth on the previous day
        current_hour, current_on_duty_hour = switch_to_on_duty(
            log, current_hour, current_on_duty_hour, time_spent, action="Pre-trip/TIV"
        )
        current_hour, current_on_duty_hour, total_time_traveled = start_driving(
            log, current_hour, time_spent, current_on_duty_hour, total_time_traveled
        )

    elif (
        0 < prev_sleeper_berth_hr < MAX_SLEEPER_BERTH_TIME
    ):  # If driver has not spent up to 10 hours in sleeper berth on the previous day
        # Step 1: Start at sleeper berth until you have spent 10 hours there
        log["logbook"].append({"hour": current_hour, "row": "sleeper"})
        current_hour += MAX_SLEEPER_BERTH_TIME - prev_sleeper_berth_hr
        time_spent["sleeper"] += MAX_SLEEPER_BERTH_TIME - prev_sleeper_berth_hr
        log["logbook"].append({"hour": current_hour, "row": "sleeper"})

        current_hour, current_on_duty_hour = switch_to_on_duty(
            log, current_hour, current_on_duty_hour, time_spent, action="Pre-trip/TIV"
        )
        current_hour, current_on_duty_hour, total_time_traveled = start_driving(
            log, current_hour, time_spent, current_on_duty_hour, total_time_traveled
        )
    else:  # First day of trip
        log["logbook"].append({"hour": current_hour, "row": "off_duty"})
        current_hour += FIRST_DAY_RESUMPTION_TIME
        time_spent["off_duty"] += FIRST_DAY_RESUMPTION_TIME
        log["logbook"].append({"hour": current_hour, "row": "off_duty"})
        current_hour, current_on_duty_hour = switch_to_on_duty(
            log, current_hour, current_on_duty_hour, time_spent, action="Pre-trip/TIV"
        )
        current_hour, current_on_duty_hour, total_time_traveled = start_driving(
            log, current_hour, time_spent, current_on_duty_hour, total_time_traveled
        )

    return current_hour, current_on_duty_hour, total_time_traveled


def switch_to_on_duty(log, current_hour, current_on_duty_hour, time_spent, action):
    """Switches the log to on_duty mode and optionally starts driving."""
    log["logbook"].append({"hour": current_hour, "row": "on_duty"})
    current_hour += 0.5
    time_spent["on_duty"] += 0.5
    current_on_duty_hour += 0
    log["logbook"].append({"hour": current_hour, "row": "on_duty", "action": action})

    return current_hour, current_on_duty_hour


def start_driving(
    log, current_hour, time_spent, current_on_duty_hour, total_time_traveled
):
    """Handles the transition from on_duty to driving."""
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
        log["logbook"].append({"hour": current_hour, "row": "off_duty"})
        current_hour += 0.5
        time_spent["off_duty"] += 0.5
        time_traveled_within_eight_hrs = 0
        log["logbook"].append(
            {"hour": current_hour, "row": "off_duty", "action": "30-minute break"}
        )
        current_hour, current_on_duty_hour, total_time_traveled = start_driving(
            log, current_hour, time_spent, current_on_duty_hour, total_time_traveled
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
        miles_traveled = 0
        time_traveled_within_eight_hrs = 0
        current_hour, current_on_duty_hour = switch_to_on_duty(
            log, current_hour, current_on_duty_hour, time_spent, action="Refuelling"
        )
        current_hour, current_on_duty_hour, total_time_traveled = start_driving(
            log, current_hour, time_spent, current_on_duty_hour, total_time_traveled
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

        logbooks = start_new_day(
            log,
            duration,
            total_time_minutes,
            total_distance_miles,
            total_time_traveled,
            miles,
            logbooks,
            current_hour,
            time_spent,
            prev_has_arrived_at_pickup
        )
    return current_hour, logbooks


def start_new_day(
    log,
    duration,
    total_time_minutes,
    total_distance_miles,
    total_time_traveled,
    miles,
    logbooks, 
    current_hour,
    time_spent,
    prev_has_arrived_at_pickup = False,
):
    """Starts a new day of logging."""
    time_to_stay_in_sleeper_berth = 24 - current_hour
    current_hour += time_to_stay_in_sleeper_berth
    time_spent["sleeper"] += time_to_stay_in_sleeper_berth
    log["logbook"].append({"hour": current_hour, "row": "sleeper"})


    next_day_log = auto_fill_logbook(
        duration,
        total_time_minutes,
        total_distance_miles,
        total_time_traveled,
        time_to_stay_in_sleeper_berth,
        miles,
        prev_has_arrived_at_pickup,
    )
    logbooks += next_day_log
    return logbooks


def arrive_at_location(
    log, current_hour, time_spent, current_on_duty_hour, total_time_traveled, action
):
    """Handles arrival at a location."""
    current_hour, current_on_duty_hour = switch_to_on_duty(
        log, current_hour, current_on_duty_hour, time_spent, action="Refuelling"
    )
    current_hour, current_on_duty_hour, total_time_traveled = start_driving(
            log, current_hour, time_spent, current_on_duty_hour, total_time_traveled
        )
    return current_hour, current_on_duty_hour, total_time_traveled


def end_trip(log, current_hour, time_spent):
    """Handles end of the trip and switching to off_duty."""
    log["logbook"].append({"hour": current_hour, "row": "off_duty"})
    remaining_hour = 24 - current_hour
    current_hour += remaining_hour
    time_spent["off_duty"] += remaining_hour
    log["logbook"].append({"hour": current_hour, "row": "off_duty"})

    return current_hour
