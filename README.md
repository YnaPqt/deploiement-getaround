
![2bd4cdf9-37f2-497f-9096-c2793296a75f-1568844229943](https://github.com/user-attachments/assets/9e841707-2257-46fc-94b4-229d9a349016)

# GetAround 
GetAround is a car-sharing platform that allows individuals to rent cars from private owners for periods ranging from a few hours to several days. The company has experienced rapid growth, counting over 5 million users and approximately 20,000 cars worldwide as of 2019.

As part of this project, participants are expected to conduct data analysis and build machine learning services to support GetAround’s business decisions.

## Context 

When a rental occurs, users must complete a check-in flow at the start and a checkout flow at the end to:

  - Assess the vehicle’s condition and report any pre-existing or new damages.

  - Compare fuel levels.

  - Record the number of kilometers driven.

Rentals can follow one of three flows:

  - Mobile: The driver and owner meet in person and sign the rental agreement on the owner’s smartphone.

  - Connect: The driver unlocks the car remotely via smartphone without meeting the owner.

  - Paper contract: A negligible fraction of agreements are still on paper.

## Project Goals🚧

Participants must analyze late vehicle returns, which disrupt subsequent rentals and impact customer satisfaction. Late returns sometimes force the next renter to wait or even cancel their booking.

To mitigate this, GetAround plans to implement a minimum delay between rentals so that a vehicle cannot be booked if the check-in or checkout times are too close to another reservation. However, this measure could reduce owner and platform revenues. Therefore, the right trade-off must be identified.

The Product Manager requires data insights to inform the following decisions:

- Threshold: How long should the minimum delay be?

- Scope: Should the feature be applied to all cars or only to Connect-enabled cars?

Participants are expected to address these questions:

- What share of owner revenue would potentially be affected by this feature?

- How many rentals would be impacted by the feature, based on different thresholds and scopes?

- How often are drivers late, and how does lateness impact subsequent rentals?

- How many problematic cases would this feature solve, depending on the chosen parameters?
