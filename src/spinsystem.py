import math
from random import Random
import numpy as np

class SpinSystem:
    def __init__(self, random_generator, num_groups, num_spins_per_group, T, J, nu, p_spin_up=0.5, time_delay=0, dynamics='metropolis'):
        self.random_generator = random_generator
        self.num_groups = num_groups
        self.num_spins_per_group = num_spins_per_group
        self.T = T  # Temperature
        self.J = J  # Coupling constant
        self.nu = nu  # Angular dependence exponent
        self.p_spin_up = p_spin_up  # Probability of spin being 1 (up)
        self.spins = np.array([[1 if Random.uniform(self.random_generator, 0, 1) < self.p_spin_up else 0
                                for _ in range(self.num_spins_per_group)] for _ in range(self.num_groups)])
        self.time_delay = time_delay
        self.spins_history = np.array([self.spins])
        self.dynamics = dynamics # Dynamics type: 'metropolis' or 'glauber'
        # Assigning one unique angle to each group, replicated for each spin
        group_angles = np.linspace(0, 2 * math.pi, num_groups, endpoint=False)
        self.angles = np.repeat(group_angles, self.num_spins_per_group)  # This ensures angles are 1D
        self.external_field = np.zeros(self.num_groups * self.num_spins_per_group)  # Placeholder for external field strengths

    def calculate_hamiltonian(self, state=None):
        """ Calculate the Hamiltonian using the provided state or the historical state if none provided. """
        if state is None:
            if not self.spins_history:  # Check if the deque is empty
                raise ValueError("Spin history is unexpectedly empty")
            state_to_use = self.spins_history[0]  # Always use the oldest state in the history
        else:
            state_to_use = state  # Use the provided state

        J_matrix = self.calculate_j_matrix()
        spin_interaction_matrix = np.outer(state_to_use.flatten(), state_to_use.flatten())
        H_spin_interactions = -(self.J / (self.num_spins_per_group * self.num_groups)) * (J_matrix * spin_interaction_matrix)
        # include diagonal or not?
        H_spin_interactions = np.sum(np.triu(H_spin_interactions, 1))  # Sum only the upper triangle to avoid double counting

        # Adding external field contribution
        external_field_contribution = -np.sum(self.external_field * state_to_use.flatten())

        return H_spin_interactions + external_field_contribution

    def calculate_j_matrix(self):
        """
        Calculate the interaction matrix J based on angular differences using the class attributes.
        """
        # Calculate the absolute difference in angles between each pair of spins
        angle_diff_matrix = np.abs(np.subtract.outer(self.angles, self.angles))

        # Adjust differences to be within [0, pi]
        angle_diff_matrix = np.minimum(angle_diff_matrix, 2 * math.pi - angle_diff_matrix)
        # Normalize differences by pi, raise to the power nu, and apply cosine
        J_matrix = np.cos(math.pi * ((angle_diff_matrix / math.pi) ** self.nu))
        
        return J_matrix

    def step(self, timedelay=True,dt=0.1, tau=33):
        """ Perform one Metropolis step, optionally using a hybrid historical state or the current state. """
        # Select a random spin
        i = Random.randint(self.random_generator,0,self.num_groups-1)
        j = Random.randint(self.random_generator,0,self.num_spins_per_group-1)
        if timedelay:
            # Create a hybrid state using the latest historical state
            hybrid_state = self.spins_history[-1]
            hybrid_state[i, j] = self.spins[i, j]  # Update the specific spin to its current state
            state_to_use = hybrid_state
        else:
            # Use the current state directly
            state_to_use = self.spins

        # Calculate current Hamiltonian using the selected state
        current_hamiltonian = self.calculate_hamiltonian(state_to_use)
        
        # Propose flipping the spin
        state_to_use[i, j] ^= 1
        
        # Calculate new Hamiltonian with the flipped spin
        new_hamiltonian = self.calculate_hamiltonian(state_to_use)
        
        # Calculate change in Hamiltonian
        delta_h = new_hamiltonian - current_hamiltonian

            # Determine acceptance based on dynamics
        if self.dynamics == 'metropolis':
            self._metropolis_acceptance(i, j, delta_h)
        elif self.dynamics == 'glauber':
            self._glauber_acceptance(i, j, delta_h, dt, tau)
        else:
            raise ValueError(f"Unknown dynamics type: {self.dynamics}")

        # Update the history with every metropolis step regardless of timedelay
        self.spins_history = np.append(self.spins_history,[self.spins],axis=0)

    def _metropolis_acceptance(self, i, j, delta_h):
        """Metropolis acceptance condition."""
        if delta_h <= 0 or Random.uniform(self.random_generator,0,1) < np.exp(-delta_h / self.T):
            # Accept the spin flip
            self.spins[i, j] ^= 1
    
    def _glauber_acceptance(self, i, j, delta_h, dt, tau):
        """Glauber acceptance condition."""
        G = self.num_groups
        N = self.num_spins_per_group
        # Calculate the acceptance probability
        acceptance_prob = (G * N * dt) / tau * (1 / (1 + np.exp(delta_h / self.T)))

        # Ensure acceptance probability does not exceed 1
        acceptance_prob = min(acceptance_prob, 1.0)

        # Acceptance condition
        if Random.uniform(self.random_generator,0,1) < acceptance_prob:
            # Accept the spin flip
            self.spins[i, j] ^= 1

    def run_simulation(self, steps=1, dt=None, tau=None):
        for _ in range(steps):
            self.step(dt=dt, tau=tau)
        return self.spins
    
    #maybe add circ.stats in the future
    def average_direction_of_activity(self):
        # Flatten the spins array and get the angles corresponding to each spin
        flattened_spins = self.spins.flatten()
        # If all spins are active, return None
        if np.all(flattened_spins == 1):
            return None

        # Applica la rotazione dell'orientamento
        unit_vectors = np.exp(1j * self.angles)  # Complex numbers representing unit vectors

        # Mask to select only spins with state 1
        active_mask = flattened_spins == 1

        # Calculate the average direction by summing unit vectors with active mask
        sum_vector = np.sum(unit_vectors[active_mask])

        # Normalize to get the unit direction
        if sum_vector != 0:
            avg_direction = np.angle(sum_vector)  # Returns the angle in radians
        else:
            avg_direction = None  # No active spins

        return avg_direction
    
    def get_inverse_magnitude_of_activity(self):
        """
        Calculate the magnitude of the summed vectors of active spins, normalized by total number of spins.
        """
        # Flatten the spins array and get the angles corresponding to each spin
        flattened_spins = self.spins.flatten()
        unit_vectors = np.exp(1j * self.angles.flatten())  # Complex numbers representing unit vectors

        # Mask to select only spins with state 1
        active_mask = flattened_spins == 1

        # Calculate the sum of unit vectors for active spins
        sum_vector = np.sum(unit_vectors[active_mask])

        # Calculate magnitude
        magnitude = abs(sum_vector)
        
        inverse_magnitude = 1/magnitude
  
        return inverse_magnitude
    
    def get_width_of_activity(self):
        """
        Calculate the width of the peak of activity by measuring the dispersion of active spin directions.
        """
        # Flatten the spins array and get the angles corresponding to each spin
        flattened_spins = self.spins.flatten()
        angles = self.angles.flatten()
        # Mask to select only spins with state 1
        active_mask = flattened_spins == 1
        active_angles = angles[active_mask]

        if len(active_angles) > 1:
            # Compute the mean resultant length R
            unit_vectors = np.exp(1j * active_angles)
            R = abs(np.mean(unit_vectors))
            # Circular standard deviation can be approximated by sqrt(-2 * ln(R))
            if R > 0:
                circ_std = math.sqrt(-2 * math.log(R))
            else:
                circ_std = math.pi  # Maximum possible dispersion
            return circ_std
        else:
            return None  # Not enough active spins to compute width
    

    def update_external_field(self, perceptual_outputs):
        """ Update external magnetic field strengths based on perceptual system outputs. """
        self.external_field = perceptual_outputs

    def get_states(self):
        """Return the current spin states in their original matrix form."""
        return self.spins
    
    def set_states(self, states):
        """Set the spin states directly from an external source."""
        if states.shape != self.spins.shape:
            raise ValueError(f"Invalid shape for spin states. Expected {self.spins.shape}, but got {states.shape}.")
        self.spins = states  # Set the spins to the provided states
        self.spins_history = np.append(self.spins_history,[self.spins],axis=0)


    def sense_other_ring(self, other_ring_states, gain=1.0):
        """
        Compute the external field contribution from another ring's spin states.
        This is similar to how the perception system produces an external field,
        but here the 'stimulus' is the other ring's state.

        :param other_ring_states: A 2D array of shape (num_groups, num_spins_per_group)
                                or a 1D array already flattened.
        :param gain: A scalar that can be positive (excitatory) or negative (inhibitory).
        :return: A 1D external field array of length (num_groups * num_spins_per_group).
        """
        # Make sure we have a 1D array
        flat_states = other_ring_states.flatten()

        # Example approach:
        #     - If your spins are in {0,1}, you might want to transform them to [-1,+1] 
        #       so that a "flip" is truly inhibitory vs excitatory. For example:
        #             spin_value = 2*spin - 1
        #       That is optional and depends on how you want to model the coupling.
        #     - If you prefer direct usage of {0,1}, you can keep it simpler.
        # 
        # Here we transform [0,1] → [-1,+1]:
        #transformed = 2.0 * flat_states - 1.0
        #i try without transformation
        transformed = flat_states
        
        # Multiply by gain
        external_field = gain * transformed

        self.external_field = external_field

