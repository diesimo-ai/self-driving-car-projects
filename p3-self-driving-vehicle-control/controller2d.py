#!/usr/bin/env python3

"""
2D Controller Class to be used for the CARLA waypoint follower demo.
"""

import cutils
import numpy as np
# import cvxpy as cp

class PIDController:
    """
    - PID controller Implementation

        - kp : speed 
        - ki : accuracy (e = 0)
        - kd : stability
            - these coefs are tuned manually to find an optimal values i.e : error ~ 0 
            - they can also be adjusted automatically using algorithms such as the Ziegler-Nichols method.
    """
    def __init__(self, kp=0.0, ki=0.0, kd=0.0):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.integral_error = 0.0
        self.previous_error = 0.0

    def update(self, error, dt):
        # Calculate proportional error
        p_error = error

        # Calculate integral error
        self.integral_error += error * dt
        i_error = self.integral_error

        # Calculate derivative error
        d_error = (error - self.previous_error) / dt

        # Update previous error for next iteration
        self.previous_error = error

        # Calculate control output using PID formula
        output = (self.kp * p_error) + (self.ki * i_error) + (self.kd * d_error)

        return output

class PurePursuitController:
    """
        - Btw :  
        - Geometric Lateral Control : slow speed and planned trajectory
            - Pure Pursuit 
            - Stanley
        - Dynamic Model Predictive Control (MPC) : high speed and slipery 
                            
    """    
    def __init__(self, L):
        self.L = L

    def get_control(self, x, y, yaw, v, waypoints):
        # Find the current waypoint
        min_dist = float('inf')
        min_index = -1
        n_points = len(waypoints)
        for i in range(n_points):
            dx = waypoints[i][0] - x
            dy = waypoints[i][1] - y
            dist = np.sqrt(dx**2 + dy**2)
            if dist < min_dist:
                min_dist = dist
                min_index = i

        # Find the lookahead point
        lookahed_index = min_index + 1
        if lookahed_index >= n_points:
            lookahed_index -= n_points

        # Compute the control law
        alpha = np.atan2(waypoints[lookahed_index][1] - y,
                           waypoints[lookahed_index][0] - x) - yaw

        curvature = 2*np.sin(alpha)/min_dist
        steering_angle = np.atan(curvature*self.L)

        return steering_angle

class StanleyController:
    """
    references : https://medium.com/roboquest/understanding-geometric-path-tracking-algorithms-stanley-controller-25da17bcc219
    """
    def __init__(self, k, ks):
        self.k  = k
        self.ks = ks        # to adjust the controller in case of disturbance
   
    def control(self, x, y, yaw, v, waypoints):
        # heading error
        yaw_path = np.arctan2(waypoints[-1][1]-waypoints[0][1], waypoints[-1][0]-waypoints[0][0])
        # yaw_path = np.arctan2(slope, 1.0)  # This was turning the vehicle only to the right (some error)
        yaw_diff_heading = yaw_path - yaw 
        if yaw_diff_heading > np.pi:
            yaw_diff_heading -= 2 * np.pi
        if yaw_diff_heading < - np.pi:
            yaw_diff_heading += 2 * np.pi

        # crosstrack erroe
        current_xy = np.array([x, y])
        crosstrack_error = np.min(np.sum((current_xy - np.array(waypoints)[:, :2])**2, axis=1))
        yaw_cross_track = np.arctan2(y-waypoints[0][1], x-waypoints[0][0])
        yaw_path2ct = yaw_path - yaw_cross_track
        
        if yaw_path2ct > np.pi:
            yaw_path2ct -= 2 * np.pi
        if yaw_path2ct < - np.pi:
            yaw_path2ct += 2 * np.pi
        if yaw_path2ct > 0:
            crosstrack_error = abs(crosstrack_error)
        else:
            crosstrack_error = - abs(crosstrack_error)
        yaw_diff_crosstrack = np.arctan(self.k  * crosstrack_error /(self.k + v))  # ks=1 to avoid zero division if v= 0 

        # final expected steering
        steer_expect = yaw_diff_crosstrack + yaw_diff_heading
        if steer_expect > np.pi:
            steer_expect -= 2 * np.pi
        if steer_expect < - np.pi:
            steer_expect += 2 * np.pi
        steer_expect = min(1.22, steer_expect)
        steer_expect = max(-1.22, steer_expect)

        #update
        steer_output = steer_expect

        return steer_output

# class StanleyController:
#     def __init__(self, k, ks):
#         self.k  = k
#         self.ks = ks        # to adjust the controller in case of disturbance

#         # self.delta = float('inf')

#     def control(self, x, y, yaw, v, waypoints):
#         # Find the current waypoint
#         min_dist = float('inf')
#         min_index = 0
#         n_points = len(waypoints)
#         front_x = x + self.k*np.cos(yaw)
#         front_y = y + self.k*np.sin(yaw)
        
#         for i in range(n_points):
#             dx = front_x - waypoints[i][0]
#             dy = front_y - waypoints[i][1]
#             dist = np.sqrt(dx**2 + dy**2)
            
#             if dist < min_dist:
#                 min_dist = dist
#                 min_index = i
        
#         # Compute the cross track error
#         current_waypoint_x = waypoints[min_index][0]
#         current_waypoint_y = waypoints[min_index][1]
        
#         dxl = current_waypoint_x - x
#         dyl = current_waypoint_y - y

#         # Compute the heading error
#         target_yaw    = np.arctan2(dyl,dxl)
#         heading_error = target_yaw - yaw
#         # steering angle is bounded btw [min and max], therefore [-pi, +pi]   
#         if heading_error > np.pi:
#             heading_error -= 2 * np.pi
#         if heading_error < - np.pi:
#             heading_error += 2 * np.pi   

#         # cross track error equation
#         crosstrack_error = np.sin(yaw + np.pi/2)*(x - current_waypoint_x) - np.cos(yaw + np.pi/2)*(y - current_waypoint_y)

#         # if dx == 0: 
#         #     yaw_path_rad = + np.pi/2 if dy > 0 else -np.pi/2 
        
#         #     yaw_path_rad2 = target_yaw - yaw_path_rad
#         #     if yaw_path_rad2 > np.pi:
#         #         yaw_path_rad2 -= 2 * np.pi
#         #     if yaw_path_rad2 < - np.pi:
#         #         yaw_path_rad2 += 2 * np.pi
#         #     if yaw_path_rad2 > 0:        
#         #         crosstrack_error = abs(crosstrack_error)
#         #     else:
#         #         crosstrack_error = - abs(crosstrack_error)

#         # Compute the steering angle
#         delta = heading_error + np.arctan(self.k*crosstrack_error/(self.ks + v))
#         # limit
#         if delta > np.pi:
#             delta -= 2 * np.pi
#         if delta < - np.pi:
#             delta += 2 * np.pi
#         delta = min(1.22, delta)
#         delta = max(-1.22, delta)

#         return delta        

    
    # def get_delta(self):
    #     pass

    # def get_heading_error(self):
    #     pass

    # def get_cross_track_error(self):
    #     pass 


# class StanleyController:
#     """
#     - StanleyController with a constructor that takes as input the gain parameter k 
#     - and a method control that takes as input the current position (x,y), orientation yaw, speed v 
#     - and a list of waypoints. The method computes the cross track error (cte) between the current position 
#     - and the closest waypoint    
    
#     """
#     def __init__(self, k):
#         self.k = k
#         self.delta = float('inf')

#     def control(self, x, y, yaw, v, waypoints):
#         # Find the current waypoint
#         min_d = float('inf')
#         min_i = 0
#         n_points = len(waypoints)
        
#         for i in range(n_points):
#             dx = x - waypoints[i][0]
#             dy = y - waypoints[i][1]
#             d = np.sqrt(dx**2 + dy**2)
            
#             if d < min_d:
#                 min_d = d
#                 min_i = i
        
#         # Compute cross track error (cte)
#         fx = waypoints[min_i][0]
#         fy = waypoints[min_i][1]
                
#         cte_vec_x = fy - y
#         cte_vec_y = -(fx - x)
        
#         cte_dot = cte_vec_x * np.cos(yaw + np.pi/2) + cte_vec_y * np.sin(yaw + np.pi/2)

#     def get_delta(self):
#         return self.delta


class MPC:
    def __init__(self, A, B, Q, R, N):
        self.A = A
        self.B = B
        self.Q = Q
        self.R = R
        self.N = N

    def solve(self, x0):
        x = cp.Variable((self.A.shape[0], self.N + 1))
        u = cp.Variable((self.B.shape[1], self.N))

        cost = 0
        constraints = [x[:,0] == x0]
        for t in range(self.N):
            cost += cp.quad_form(x[:,t], self.Q) + cp.quad_form(u[:,t], self.R)
            constraints += [x[:,t+1] == self.A @ x[:,t] + self.B @ u[:,t]]
        
        cost += cp.quad_form(x[:,-1], self.Q)

        prob = cp.Problem(cp.Minimize(cost), constraints)
        prob.solve()

        return u[:,0].value

# A = np.array([[1.0]])
# B = np.array([[1.0]])
# Q = np.array([[1.0]])
# R = np.array([[1.0]])
# N = 10

# mpc_controller = MPC(A,B,Q,R,N)

# x0 = np.array([10.])
# u_optimal= mpc_controller.solve(x0)

class Controller2D(object):
    def __init__(self, waypoints):
        self.vars                = cutils.CUtils()
        self._current_x          = 0
        self._current_y          = 0
        self._current_yaw        = 0
        self._current_speed      = 0
        self._desired_speed      = 0
        self._current_frame      = 0
        self._current_timestamp  = 0
        self._start_control_loop = False
        self._set_throttle       = 0
        self._set_brake          = 0
        self._set_steer          = 0
        self._waypoints          = waypoints
        self._conv_rad_to_steer  = 180.0 / 70.0 / np.pi
        self._pi                 = np.pi
        self._2pi                = 2.0 * np.pi

    def update_values(self, x, y, yaw, speed, timestamp, frame):
        self._current_x         = x
        self._current_y         = y
        self._current_yaw       = yaw
        self._current_speed     = speed
        self._current_timestamp = timestamp
        self._current_frame     = frame
        if self._current_frame:
            self._start_control_loop = True

    def update_desired_speed(self):
        min_idx       = 0
        min_dist      = float("inf")
        desired_speed = 0
        for i in range(len(self._waypoints)):
            dist = np.linalg.norm(np.array([
                    self._waypoints[i][0] - self._current_x,
                    self._waypoints[i][1] - self._current_y]))
            if dist < min_dist:
                min_dist = dist
                min_idx = i
        if min_idx < len(self._waypoints)-1:
            desired_speed = self._waypoints[min_idx][2]
        else:
            desired_speed = self._waypoints[-1][2]
        self._desired_speed = desired_speed

    def update_waypoints(self, new_waypoints):
        self._waypoints = new_waypoints

    def get_commands(self):
        return self._set_throttle, self._set_steer, self._set_brake

    def set_throttle(self, input_throttle):
        # Clamp the throttle command to valid bounds
        throttle           = np.fmax(np.fmin(input_throttle, 1.0), 0.0)
        self._set_throttle = throttle

    def set_steer(self, input_steer_in_rad):
        # Covnert radians to [-1, 1]
        input_steer = self._conv_rad_to_steer * input_steer_in_rad

        # Clamp the steering command to valid bounds
        steer           = np.fmax(np.fmin(input_steer, 1.0), -1.0)
        self._set_steer = steer

    def set_brake(self, input_brake):
        # Clamp the steering command to valid bounds
        brake           = np.fmax(np.fmin(input_brake, 1.0), 0.0)
        self._set_brake = brake

    def update_controls(self):
        ######################################################
        # RETRIEVE SIMULATOR FEEDBACK
        ######################################################
        x               = self._current_x
        y               = self._current_y
        yaw             = self._current_yaw
        v               = self._current_speed
        self.update_desired_speed()
        v_desired       = self._desired_speed
        t              = self._current_timestamp
        waypoints       = self._waypoints
        throttle_output = 0
        steer_output    = 0
        brake_output    = 0

        ######################################################
        ######################################################
        # MODULE 7: DECLARE USAGE VARIABLES HERE
        ######################################################
        ######################################################
        """
            Use 'self.vars.create_var(<variable name>, <default value>)'
            to create a persistent variable (not destroyed at each iteration).
            This means that the value can be stored for use in the next
            iteration of the control loop.

            Example: Creation of 'v_previous', default value to be 0
            self.vars.create_var('v_previous', 0.0)

            Example: Setting 'v_previous' to be 1.0
            self.vars.v_previous = 1.0

            Example: Accessing the value from 'v_previous' to be used
            throttle_output = 0.5 * self.vars.v_previous
        """
        self.vars.create_var('x_previous', 0.0)
        self.vars.create_var('y_previous', 0.0)
        self.vars.create_var('v_previous', 0.0)
        self.vars.create_var('v_previous', 0.0)
        self.vars.create_var('throttle_previous', 0.0)
        self.vars.create_var('yaw_previous', 0.0)

        # Skip the first frame to store previous values properly
        if self._start_control_loop:
            """
                Controller iteration code block.

                Controller Feedback Variables:
                    x               : Current X position (meters)
                    y               : Current Y position (meters)
                    yaw             : Current yaw pose (radians)
                    v               : Current forward speed (meters per second)
                    t               : Current time (seconds)
                    v_desired       : Current desired speed (meters per second)
                                      (Computed as the speed to track at the
                                      closest waypoint to the vehicle.)
                    waypoints       : Current waypoints to track
                                      (Includes speed to track at each x,y
                                      location.)
                                      Format: [[x0, y0, v0],
                                               [x1, y1, v1],
                                               ...
                                               [xn, yn, vn]]
                                      Example:
                                          waypoints[2][1]: 
                                          Returns the 3rd waypoint's y position

                                          waypoints[5]:
                                          Returns [x5, y5, v5] (6th waypoint)
                
                Controller Output Variables:
                    throttle_output : Throttle output (0 to 1)
                    steer_output    : Steer output (-1.22 rad to 1.22 rad)
                    brake_output    : Brake output (0 to 1)
            """

            ######################################################
            ######################################################
            # MODULE 7: IMPLEMENTATION OF LONGITUDINAL CONTROLLER HERE
            ######################################################
            ######################################################
            """
                Implement a longitudinal controller here. Remember that you can
                access the persistent variables declared above here. For
                example, can treat self.vars.v_previous like a "global variable".               
            """
            # Change these outputs with the longitudinal controller. 
            # Note that brake_output is optional and is not required to pass the
            # assignment, as the car will naturally slow down over time.
            
            # Phase 1 - Upper Controller : Vdes => Ades
            # Phase 2 - Lower Controller : Ades => throttle_output
            brake_input     = 0
            throttle_input  = 0
            # create longitudinal controller object
            # kp, ki, kd=(1.0, 0.5, 0.1)
            # kp, ki, kd=(1.0, 0.5, 0.1)
            # kp, ki, kd=(1.0, 0.5, 0.1)
            long_controller = PIDController(kp=1.0, ki=0.2, kd=0.01)
            # Calculate speed error and update PID controller
            speed_error = v_desired - v
            pid_output = long_controller.update(speed_error, t)

            # control logic
            # if pid_output > 0:
            #     throttle_output = pid_output
            #     brake_input = 0
            # else:
            #     throttle_input = 0
            #     brake_output = -pid_output
            if pid_output > 0:
                throttle_output = (np.tanh(pid_output) + 1)/2
                # throttle_output = max(0.0, min(1.0, throttle_output))
                if throttle_output - self.vars.throttle_previous > 0.1:
                    throttle_output = self.vars.throttle_previous + 0.1
            else:
                throttle_output = 0

            ######################################################
            ######################################################
            # MODULE 7: IMPLEMENTATION OF LATERAL CONTROLLER HERE
            ######################################################
            ######################################################
            """
                Implement a lateral controller here. Remember that you can
                access the persistent variables declared above here. For
                example, can treat self.vars.v_previous like a "global variable".

            """
            # PurePursuitController lateral controller. 
            # L = self._current_frame 
            # lateral_controller = PurePursuitController(L)
            # steer_output = lateral_controller.get_control(x, y, yaw, v, waypoints)
            steer_output = 0
            # StanleyController lateral controller. 
            # k how agressive the controller responds to cte has to be tunned  : 
            # k= [0.5, 0.4, 0.3, 0.2 0.1]
            # ks : proportional control to steering angle has to be tunned  
            # ks= [1 2, 3, 4, 5]
            lateral_controller = StanleyController(k=0.3, ks=1)
            #  set input values to the compute the steering angle
            steer_output = lateral_controller.control(x, y, yaw, v, waypoints) 
            # get steering angle
            # steer_output = lateral_controller.get_delta()           
            
            ######################################################
            # SET CONTROLS OUTPUT
            ######################################################
            self.set_throttle(throttle_output)  # in percent (0 to 1)
            self.set_steer(steer_output)        # in rad (-1.22 to 1.22)
            self.set_brake(brake_output)        # in percent (0 to 1)

        ######################################################
        ######################################################
        # MODULE 7: STORE OLD VALUES HERE (ADD MORE IF NECESSARY)
        ######################################################
        ######################################################
        """
            Use this block to store old values (for example, we can store the
            current x, y, and yaw values here using persistent variables for use
            in the next iteration)
        """
        # Store forward speed to be used in next step        
        self.vars.x_previous = x
        self.vars.y_previous = y 
        self.vars.v_previous = v  
        self.vars.throttle_previous = throttle_output
        self.vars.v_desired_previous = v_desired
        self.vars.yaw_previous = yaw



