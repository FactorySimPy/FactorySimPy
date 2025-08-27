# Selective Interruption Implementation Documentation

## Overview
The selective interruption feature allows the conveyor belt to interrupt only specific items based on their actual positions on the belt, determined by their `conveyor_entry_time`.

## Key Concepts

### Pattern Representation
- `*` = Position with an item (occupied)
- `_` = Empty position (no item)

### Position Calculation
Items' positions are calculated using:
```python
time_on_belt = current_time - item.conveyor_entry_time
distance_traveled = time_on_belt * belt_speed
position_ratio = remaining_distance / total_belt_length
position_index = int(position_ratio * (capacity - 1))
```

### Interruption Rules

| Pattern | Description | Items to Interrupt | Example |
|---------|-------------|-------------------|---------|
| `*****` | Full belt | ALL items | All 5 items moving |
| `**_**` | Gap in middle | LAST 2 items | Items at positions 4,5 |
| `*_*_*` | Alternating | LAST 1 item | Item at position 5 |
| `*__**` | Gap after first | LAST 2 items | Items at positions 4,5 |
| `**___` | Items at start | ALL moving items | Items at positions 1,2 |
| `___**` | Items at end | LAST 2 items | Items at positions 4,5 |

## Implementation Details

### Core Methods

1. **`get_belt_occupancy_pattern()`**
   - Analyzes item positions based on `conveyor_entry_time`
   - Returns pattern string (e.g., `"**_**"`)

2. **`get_items_to_interrupt()`**
   - Determines which items should be interrupted
   - Based on pattern analysis and interruption rules

3. **`interrupt_selective_move_processes()`**
   - Interrupts only the selected items
   - Shows detailed belt status for debugging

4. **`show_belt_status()`**
   - Displays current belt state
   - Shows item positions and timing information

### Integration with Conveyor

```python
# In ConveyorBelt.set_conveyor_state()
if new_state == "STALLED_NONACCUMULATING_STATE":
    # Use selective interruption based on occupancy pattern
    self.belt.interrupt_selective_move_processes(f"Conveyor {self.id} stalled")
```

## Usage Example

```python
# Create conveyor
conveyor = ConveyorBelt(env, "conv1", capacity=5, speed=1.0, length=10.0, accumulating=0)

# Add items at different times
item1 = Item("item1")
item1.conveyor_entry_time = 10.0  # Entered at T=10
item2 = Item("item2") 
item2.conveyor_entry_time = 15.0  # Entered at T=15

# At T=20, trigger selective interruption
conveyor.set_conveyor_state("STALLED_NONACCUMULATING_STATE")
# Only items in moving positions will be interrupted

# Resume all interrupted items
conveyor.set_conveyor_state("MOVING_STATE")
```

## Testing

The `test_selective_interrupt.py` file provides comprehensive tests for:
- Various occupancy patterns
- Realistic timing scenarios
- Dynamic interruption during simulation

Run tests with:
```bash
python examples/test_selective_interrupt.py
```

## Benefits

1. **Realistic Behavior** - Only moving items are affected by stalls
2. **Efficient Processing** - Stationary items continue unaffected  
3. **Accurate Simulation** - Based on actual physics of conveyor movement
4. **Debug Support** - Detailed status visualization
5. **Flexible Control** - Pattern-based interruption rules
