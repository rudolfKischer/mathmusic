from numpy import array, linalg
from waves import get_oscillator_sound_function

def draw_visualizer_line(graph, start, end, color):
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
    extension = 2
    extended_end = end + extension * direction
    graph.draw_line(tuple(start), tuple(extended_end), color=color, width=3)


def get_sample_visualizer_point(window_pos, window_offset, window_duration, soundFunction):


    sample_x = window_duration * window_pos + window_offset

    sample_y = soundFunction(sample_x)

    return (sample_x, sample_y)


def get_screen_point_seg(sample, normalized_pos, width, height, vis_num, vis_total):
    relative_vert = vis_num / float(vis_total)

    sample_y = sample[1]
    screen_x = normalized_pos * width
    screen_y = ((sample_y + 1) * 0.5 * (1 / float(vis_total)) + relative_vert) * height
    return (screen_x, screen_y)

def draw_visualizer_seg(graph, window_duration, window_offset, sample_rate, soundFunction, vis_num, vis_total, color="green"):
    global visualizerPhase
    width = graph.CanvasSize[0]
    height = graph.CanvasSize[1]
    
    for sampleNum in range(0,int(sample_rate)):
        
        start_relative_pos = sampleNum / float(sample_rate)
        end_relative_pos = (sampleNum + 1) / float(sample_rate)

        start = get_sample_visualizer_point(start_relative_pos, window_offset, window_duration, soundFunction)
        start = get_screen_point_seg(start, start_relative_pos, width, height, vis_num, vis_total)

        end = get_sample_visualizer_point(end_relative_pos, window_offset, window_duration, soundFunction)
        end = get_screen_point_seg(end, end_relative_pos, width, height, vis_num, vis_total)

        draw_visualizer_line(graph, start, end, color)

def draw_visualizer(graph, window_duration, window_offset, sample_rate, soundFunction):
    graph.erase()
    draw_visualizer_seg(graph, window_duration, window_offset, sample_rate, soundFunction, 0, 1)

def draw_all_visualizer_segs(graphs, window_duration, visualizerPhase, v_num_of_samples, osci, frequency):
    len_osci = len(osci.keys())
    if len_osci != 0:
        graphs.erase()
        for i in osci.keys():
            sound_func = get_oscillator_sound_function(osci[i], frequency)
            draw_visualizer_seg(graphs, window_duration, visualizerPhase, v_num_of_samples, sound_func, i-1, (len_osci), osci[i]["color"])