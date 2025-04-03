def auto_fill_logbook(
    duration_from_current_location_to_pickup: float,
    total_time_minutes: float,
    total_distance_miles: float,
    previous_total_time_traveled: float = 0,
    prev_sleeper_berth_hr: float = 0,
    prev_miles_traveled: float = 0,
    prev_has_arrived_at_pickup: bool = False
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
    has_arrived_at_pickup = prev_has_arrived_at_pickup

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

    if prev_sleeper_berth_hr >= 10:
        # Step 1: Start at On-Duty (Vehicle Check)
        new_log["logbook"].append(
            {"hour": current_hour, "row": "on-duty", "action": "Switched to on-duty"}
        )
        current_hour += 0.5
        current_on_duty_hour += 0.5
        time_spent_in_on_duty += 0.5

        # Step 2: Stay On-Duty Before Driving
        new_log["logbook"].append(
            {"hour": current_hour, "row": "on-duty", "action": "Pre-trip/TIV"}
        )

        # Step 3: Start Driving to Pickup or drop-off
        new_log["logbook"].append({"hour": current_hour, "row": "driving"})
        current_hour += 0.5
        current_on_duty_hour += 0.5
        time_spent_in_driving += 0.5
        total_time_traveled += 0.5

        #Drive away from the location
        new_log["logbook"].append({"hour": current_hour, "row": "driving"})

    elif 0 < prev_sleeper_berth_hr < 10:

        # Step 1: Start at sleeper berth until you have spent 10 hours there
        new_log["logbook"].append({"hour": current_hour, "row": "sleeper"})
        current_hour += 10 - prev_sleeper_berth_hr
        time_spent_in_sleeper_berth += 10 - prev_sleeper_berth_hr
        new_log["logbook"].append({"hour": current_hour, "row": "sleeper"})

        # Step 2: Switch to On-Duty (Vehicle Check)
        new_log["logbook"].append({"hour": current_hour, "row": "on-duty"})
        current_hour += 0.5
        time_spent_in_on_duty += 0.5
        current_on_duty_hour += 0.5

        # Step 3: Stay On-Duty Before Driving
        new_log["logbook"].append(
            {"hour": current_hour, "row": "on-duty", "action": "Pre-trip/TIV"}
        )


        # Step 4: Start Driving to Pickup or drop-off
        new_log["logbook"].append({"hour": current_hour, "row": "driving"})
        current_hour += 0.5
        current_on_duty_hour += 0.5
        time_spent_in_driving += 0.5
        total_time_traveled += 0.5
        
        #Drive away from the location
        new_log["logbook"].append({"hour": current_hour, "row": "driving"})
    else:
        # Step 1: Start with Off-Duty until 6:30 AM
        new_log["logbook"].append({"hour": current_hour, "row": "off-duty"})
        current_hour += 6.5
        time_spent_in_off_duty += 6.5
        new_log["logbook"].append({"hour": current_hour, "row": "off-duty"})

        # Step 2: Switch to On-Duty (Vehicle Check)
        new_log["logbook"].append({"hour": current_hour, "row": "on-duty"})
        current_hour += 0.5
        time_spent_in_on_duty += 0.5
        current_on_duty_hour += 0.5

        # Step 3: Stay On-Duty Before Driving
        new_log["logbook"].append(
            {"hour": current_hour, "row": "on-duty", "action": "Pre-trip/TIV"}
        )
        # Step 4: Start Driving to Pickup
        new_log["logbook"].append({"hour": current_hour, "row": "driving"})
        current_hour += 0.5
        current_on_duty_hour += 0.5
        time_spent_in_driving += 0.5
        total_time_traveled += 0.5
        
        #Drive away from the location
        new_log["logbook"].append({"hour": current_hour, "row": "driving"})

    while total_time_traveled < duration_from_current_location_to_pickup and not has_arrived_at_pickup:
        # Base Condition: Stop Recursion if pickup location is reached.
        if total_time_traveled >= duration_from_current_location_to_pickup:
            break
        current_hour += 0.5
        current_on_duty_hour += 0.5
        new_log["logbook"].append({"hour": current_hour, "row": "driving"})
        total_time_traveled += 30
        time_traveled_within_eight_hrs += 30
        time_spent_in_driving += 0.5
        miles_traveled += (
            total_distance_miles / driving_time
        ) * 30  # Convert minutes to miles

        # Mandatory 30-min break after at least every 8 hours of driving
        if time_traveled_within_eight_hrs >= 7 * 60:
            new_log["logbook"].append({"hour": current_hour, "row": "off-duty"})
            current_hour += 0.5

            time_spent_in_off_duty += 0.5
            new_log["logbook"].append(
                {"hour": current_hour, "row": "off-duty", "action": "30-minute break"}
            )

            new_log["logbook"].append({"hour": current_hour, "row": "driving"})
            time_traveled_within_eight_hrs = 0

        # Refuelling
        if miles_traveled >= 950:
            new_log["logbook"].append({"hour": current_hour, "row": "on-duty"})
            current_hour += 0.5
            current_on_duty_hour += 0.5
            time_spent_in_on_duty += 0.5
            new_log["logbook"].append(
                {"hour": current_hour, "row": "on-duty", "action": "Refuelling"}
            )
            new_log["logbook"].append({"hour": current_hour, "row": "driving"})
            miles_traveled = 0
            time_traveled_within_eight_hrs = 0

            # Stop Driving at least every 11 total hours of driving or 14 hours of on-duty (Switch to Sleeper Berth)
        if time_spent_in_driving >= 10.5 or current_on_duty_hour >= 13.5:

            new_log["logbook"].append({"hour": current_hour, "row": "sleeper"})

            # Stay in Sleeper Berth for 10 hours
            time_to_stay_in_sleeper_berth = 24 - current_hour
            current_hour += time_to_stay_in_sleeper_berth
            time_spent_in_sleeper_berth += time_to_stay_in_sleeper_berth
            new_log["logbook"].append({"hour": current_hour, "row": "sleeper"})

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
                time_to_stay_in_sleeper_berth,
                miles_traveled,
                prev_has_arrived_at_pickup = False
            )

            return logbooks + next_day_logs  # Combine all logbooks

        # Step 5: Arrive at Pickup, Stay On-Duty for 30 minutes
    if not has_arrived_at_pickup: 
        new_log["logbook"].append({"hour": current_hour, "row": "on-duty"})

        current_hour += 0.5  # 30-minute On-Duty for Pickup
        current_on_duty_hour += 0.5
        time_spent_in_on_duty += 0.5
        time_traveled_within_eight_hrs = 0
        prev_has_arrived_at_pickup = True

        new_log["logbook"].append(
            {"hour": current_hour, "row": "on-duty", "action": "Pickup"}
        )

        # Step 6: Start Driving to Drop-off Immediately
        new_log["logbook"].append({"hour": current_hour, "row": "driving"})
        current_hour += 0.5
        current_on_duty_hour += 0.5
        time_spent_in_driving += 0.5
        total_time_traveled += 0.5
        
        #Drive away from the location
        new_log["logbook"].append({"hour": current_hour, "row": "driving"})

    # Step 7: Continue Driving to Drop-off
    while total_time_traveled < driving_time:
        # Base Condition: Stop Recursion if Trip is Done
        if total_time_traveled >= driving_time:
            break  # Trip is complete, return logs
        current_hour += 0.5
        current_on_duty_hour += 0.5
        new_log["logbook"].append({"hour": current_hour, "row": "driving"})
        total_time_traveled += 30
        time_traveled_within_eight_hrs += 30
        time_spent_in_driving += 0.5
        miles_traveled += (
            total_distance_miles / driving_time
        ) * 30  # Convert minutes to miles

        # Mandatory 30-min break after at least every 8 hours of driving
        if time_traveled_within_eight_hrs >= 7 * 60:
            new_log["logbook"].append({"hour": current_hour, "row": "off-duty"})
            current_hour += 0.5

            time_spent_in_off_duty += 0.5
            new_log["logbook"].append(
                {"hour": current_hour, "row": "off-duty", "action": "30-minute break"}
            )

            new_log["logbook"].append({"hour": current_hour, "row": "driving"})
            time_traveled_within_eight_hrs = 0

        # Refuelling
        if miles_traveled >= 950:
            new_log["logbook"].append({"hour": current_hour, "row": "on-duty"})
            current_hour += 0.5
            current_on_duty_hour += 0.5
            time_spent_in_on_duty += 0.5
            new_log["logbook"].append(
                {"hour": current_hour, "row": "on-duty", "action": "Refuelling"}
            )
            new_log["logbook"].append({"hour": current_hour, "row": "driving"})
            miles_traveled = 0
            time_traveled_within_eight_hrs = 0

        # Stop Driving at least every 11 total hours of driving or 14 hours of on-duty (Switch to Sleeper Berth)
        if time_spent_in_driving >= 10.5 or current_on_duty_hour >= 13.5:

            new_log["logbook"].append({"hour": current_hour, "row": "sleeper"})

            # Stay in Sleeper Berth for 10 hours
            time_to_stay_in_sleeper_berth = 24 - current_hour
            current_hour += time_to_stay_in_sleeper_berth
            time_spent_in_sleeper_berth += time_to_stay_in_sleeper_berth
            new_log["logbook"].append({"hour": current_hour, "row": "sleeper"})

            new_log["timeSpentInOffDuty"] = time_spent_in_off_duty
            new_log["timeSpentInOnDuty"] = time_spent_in_on_duty
            new_log["timeSpentInDriving"] = time_spent_in_driving
            new_log["timeSpentInSleeperBerth"] = time_spent_in_sleeper_berth
           
            # Start a New Day & Continue Logging (Recursive Call)
            next_day_logs = auto_fill_logbook(
                driving_time
                - total_time_traveled,  # Remaining travel time to pickup
                total_time_minutes,  # Remaining total trip time
                total_distance_miles,
                total_time_traveled,  # Keep tracking time across days
                time_to_stay_in_sleeper_berth,
                miles_traveled,
                prev_has_arrived_at_pickup
            )

            return logbooks + next_day_logs  # Combine all logbooks

    # Step 8: On-Duty at Drop-off before Sleeping
    new_log["logbook"].append({"hour": current_hour, "row": "on-duty"})

    current_hour += 0.5
    current_on_duty_hour += 0.5
    time_spent_in_on_duty += 0.5
    time_traveled_within_eight_hrs = 0
    new_log["logbook"].append(
        {"hour": current_hour, "row": "on-duty", "action": "Drop-off"}
    )

    # Step 9: Switch to off-duty (End of the Trip)
    new_log["logbook"].append({"hour": current_hour, "row": "off-duty"})

    
    remaining_hour = 24 - current_hour
    current_hour += remaining_hour
    time_spent_in_off_duty += remaining_hour
    new_log["logbook"].append({"hour": current_hour, "row": "off-duty"})

    new_log["timeSpentInOffDuty"] = time_spent_in_off_duty
    new_log["timeSpentInOnDuty"] = time_spent_in_on_duty
    new_log["timeSpentInDriving"] = time_spent_in_driving
    new_log["timeSpentInSleeperBerth"] = time_spent_in_sleeper_berth

    return logbooks  # Return multiple days of logs