from numpy import array, linalg

def draw_visualizer_line(graph, start, end):
        # Convert the start and end points to numpy arrays
    start = array(start)
    end = array(end)

    # Calculate the direction vector of the line
    direction = end - start

    # Normalize the direction vector
    norm = linalg.norm(direction)
    if norm == 0:
        return
    direction /= norm

    # Extend the line by 10 pixels in its direction of travel
    extension = 5
    extended_end = end + extension * direction
    graph.draw_line(tuple(start), tuple(extended_end), color="green", width=5)

def get_screen_point(sample, normalized_pos, width, height):
    sample_y = sample[1]
    screen_x = width * normalized_pos
    screen_y = (sample_y + 1) * 0.5 * height
    return (screen_x, screen_y)

def get_sample_visualizer_point(window_pos, window_offset, window_duration, soundFunction):


    sample_x = window_duration * window_pos + window_offset

    sample_y = soundFunction(sample_x)

    return (sample_x, sample_y)


def draw_visualizer(graph, window_duration, window_offset, sample_rate, soundFunction):
    global visualizerPhase
    width = graph.CanvasSize[0]
    height = graph.CanvasSize[1]
    graph.erase()
    
    for sampleNum in range(0,int(sample_rate)):
        
        start_relative_pos = sampleNum / float(sample_rate)
        end_relative_pos = (sampleNum + 1) / float(sample_rate)

        start = get_sample_visualizer_point(start_relative_pos, window_offset, window_duration, soundFunction)
        start = get_screen_point(start, start_relative_pos, width, height)

        end = get_sample_visualizer_point(end_relative_pos, window_offset, window_duration, soundFunction)
        end = get_screen_point(end, end_relative_pos, width, height)

        draw_visualizer_line(graph, start, end)