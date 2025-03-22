from rest_framework.response import Response
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from .models import LogEntry
from .serializers import LogSerializers
from .autofill_logbook import auto_fill_logbook  # Ensure this function is imported

class LogEntryViewSet(viewsets.ModelViewSet):
    queryset = LogEntry.objects.all()
    serializer_class = LogSerializers
    permission_classes = [permissions.AllowAny]

    @action(detail=False, methods=['post'])
    def generate_logbook(self, request):
        data = request.data
        try:
            # Extract and convert data to integers
            current_cycle_hour = int(data.get("current_cycle_hour", 0))
            total_driving_time = int(data.get("total_driving_time", 0))
            pickup_time = int(data.get("pickup_time", 0))
            total_distance_miles = int(data.get("total_distance_miles", 0))

            #  Validate input values (ensure no zero values)
            if any(val <= 0 for val in [current_cycle_hour, total_driving_time, pickup_time, total_distance_miles]):
                return Response(
                    {"error": "Invalid input values. All fields must be greater than zero.", "logbooks": []},
                    status=400
                )
            
            remaining_cycle_hours = (70 - current_cycle_hour) * 60
            pick_up_and_drop_off_time = 60 # 60 minutes
            num_fueling_stops = total_distance_miles // 1000
            total_time_to_refuel = num_fueling_stops * 30 # Assuming refuelling takes 30 minutes
            total_on_duty_time = total_driving_time + total_time_to_refuel + pick_up_and_drop_off_time
            print(f"Pickup time is {pickup_time} and Total on-duty time: {total_on_duty_time} and remaining cycle hours: {remaining_cycle_hours} and driving time is: {total_driving_time} and total time to refuel is {total_time_to_refuel}")

            if remaining_cycle_hours < total_on_duty_time:
                return Response(
                    {"error": "You do not have enough cycle hours to complete this trip", "logbooks": []},
                    status=400
                )


            #  Generate logbook data
            logbooks = auto_fill_logbook(
                current_cycle_hours=current_cycle_hour,
                total_time_minutes=total_driving_time,
                duration_from_current_location_to_pickup=pickup_time,
                total_distance_miles=total_distance_miles
            )

            return Response(logbooks)

        except ValueError:
            return Response(
                {"error": "Invalid input format. Expected numeric values.", "logbooks": []},
                status=400
            )
