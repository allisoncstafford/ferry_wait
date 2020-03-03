# Ferry Wait Predictor
Prediction engine for ferry wait times on the Washington State Ferries Edmonds-Kingston run. Based on data from December 2016 to December 2019.

## Extracting wait times from tweets:
### Assumptions:
* wait-related tweets contain the word 'wait'
* edmonds-related tweets contain the full word 'edmonds'
* kingston-related tweets contain the full word 'kingston'
* numbers are spelled out or numerals

### Standard tweet Examples:
* Edm/King - Edmonds and Kingston Terminal Status - 2 Hour Wait
* Edm/King - Kingston Terminal Status - Two Hour Wait
* Edm/King - Edmonds Terminal Status - One Hour Wait
* Edm/King - No Extended Wait for Drivers Departing Edmonds
* Edm/King - One Hour Wait Departing Kingston and Edmonds

### Non-Standard tweet Examples:
* Edm/King - Update - Edmonds and Kingston Terminal Status, 2hrs Edm, 1hr King
* Edm/King - No Extended Wait in Kingston - One Hour Wait in Edmonds, Late Vessel
* Edm/King - Kingston 6:25am Departure is Cancelled. One Hr. Wait
* Edm/King - no longer an extended wait departing edmonds or kingston
* Edm/King - edmonds and kingston terminal status - 2 hour wait
