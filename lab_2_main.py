import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import colorchooser
import numpy as np
import ctypes
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


ctypes.windll.shcore.SetProcessDpiAwareness(2)


class BezierCurve:

    def __init__(self):
        self.control_points = np.empty([0, 2])
        self.t_array = np.array([])
        self.koeff_matrix = np.array([])
        self.curve_points = np.empty([0, 2])
        self.presicion = 100

    def binom_coefficient(self, n, k):
        if k > n:
            return 0
        if n == k:
            return 1
        if k > n - k:
            k = n - k
        c = 1
        for i in range(1, k + 1):
            c *= n
            c //= i
            n -= 1
        return c

    def fill_coef_matrix(self, n):
        n -= 1
        # self.koeff_matrix = [[0] * (n + 1) for _ in range(n + 1)]
        self.koeff_matrix = np.zeros((n + 1, n + 1))

        for i in range(n + 1):
            for j in range(n + 1):
                elem = 0 if i + j > n else self.binom_coefficient(n, j) * self.binom_coefficient(n - j, n - (i + j)) * (
                    -1 if (n - (i + j)) % 2 == 1 else 1)
                self.koeff_matrix[n - i][j] = elem

    def calculate_curve_points(self):
        self.curve_points = np.empty([0, 2])
        for t in range(0, self.presicion + 1):
            t = t / self.presicion
            self.find_curve_point(t)

    def find_curve_point(self, t):
        self.get_t_array(t)
        self.curve_points = np.vstack((self.curve_points, self.t_array.dot(self.koeff_matrix.dot(self.control_points))))

    def get_curve_point(self, t):
        self.get_t_array(t)
        return self.t_array.dot(self.koeff_matrix.dot(self.control_points))

    def get_t_array(self, t):
        self.t_array = np.array([])
        for i in range(0, self.control_points.shape[0]):
            self.t_array = np.append(self.t_array, t**i)

    def get_control_points(self):
        return self.control_points

    def add_control_point(self, x, y):
        self.control_points = np.vstack((self.control_points, np.array([x, y])))
        self.update_curve()

    def update_curve(self):
        try:
            assert self.control_points.shape[0] >= 2
        except AssertionError:
            return
        else:
            self.fill_coef_matrix(self.control_points.shape[0])
            self.calculate_curve_points()

    def get_curve_points(self):
        return self.curve_points

    def get_coef_matrix(self):
        return self.koeff_matrix

    def reset_curve(self):
        self.control_points = np.empty([0, 2])
        self.curve_points = np.empty([0, 2])
        self.koeff_matrix = np.array([])

    def set_control_point(self, index, x, y):
        self.control_points[index] = [x, y]
        self.update_curve()

    def delete_control_point(self, index):
        self.control_points = np.delete(self.control_points, index, axis=0)
        self.update_curve()


class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Lab 2")

        self.scale = 10

        self.color_styles = {"points": "red", "curve": "black", "control_line": "red"}

        self.bezier_curve = BezierCurve()
        self.hold_event = None
        self.control_points = []
        self.bezier_curve_line = None
        self.bezier_curve_control_line = None

        self.controls_frame = ttk.Frame(self, borderwidth=2, relief="groove", padding=(10, 10, 10, 10))
        self.controls_frame.grid(row=0, column=2, padx=(10, 10), pady=(10, 10))

        self.controls_separator = ttk.Separator(self, orient="vertical")
        self.controls_separator.grid(row=0, rowspan=10, column=1, sticky="ns")

        self.point_coords_frame = ttk.Frame(self.controls_frame)
        self.point_coords_frame.grid(row=1, column=0, columnspan=4)

        self.draw_button = ttk.Button(self.controls_frame, text="Draw", command=self.draw_bezier_curve_action)
        self.draw_button.grid(row=0, column=0, columnspan=5)

        self.tabulate_button = ttk.Button(self.controls_frame, text="Tabulate", command=self.tabulate_window)
        self.tabulate_button.grid(row=1, column=0, columnspan=5)

        self.show_matrix_button = ttk.Button(self.controls_frame, text="Show matrix", command=self.show_matrix_window)
        self.show_matrix_button.grid(row=2, column=0, columnspan=5)

        self.color_choose_frame = ttk.Frame(self.controls_frame)
        self.color_choose_frame.grid(row=3, column=0, columnspan=5)

        self.point_color_label = ttk.Label(self.color_choose_frame, text="Point color: ")
        self.point_color_label.grid(row=0, column=0, padx=(0, 5))

        self.point_color_button = ttk.Button(self.color_choose_frame, text="Choose", command=self.choose_point_color)
        self.point_color_button.grid(row=0, column=1, padx=(0, 5))

        self.color_frame = tk.Frame(self.color_choose_frame, width=20, height=20, relief="groove", borderwidth=2, bg=self.color_styles["points"])
        self.color_frame.grid(row=0, column=2, padx=(0, 5))

        self.curve_color_label = ttk.Label(self.color_choose_frame, text="Curve color: ")
        self.curve_color_label.grid(row=1, column=0, padx=(0, 5))

        self.curve_color_button = ttk.Button(self.color_choose_frame, text="Choose", command=self.choose_curve_color)
        self.curve_color_button.grid(row=1, column=1, padx=(0, 5))

        self.curve_color_frame = tk.Frame(self.color_choose_frame, width=20, height=20, relief="groove", borderwidth=2, bg=self.color_styles["curve"])
        self.curve_color_frame.grid(row=1, column=2, padx=(0, 5))

        self.control_line_color_label = ttk.Label(self.color_choose_frame, text="Control line color: ")
        self.control_line_color_label.grid(row=2, column=0, padx=(0, 5))

        self.control_line_color_button = ttk.Button(self.color_choose_frame, text="Choose", command=self.choose_control_line_color)
        self.control_line_color_button.grid(row=2, column=1, padx=(0, 5))

        self.control_line_color_frame = tk.Frame(self.color_choose_frame, width=20, height=20, relief="groove", borderwidth=2, bg=self.color_styles["control_line"])
        self.control_line_color_frame.grid(row=2, column=2, padx=(0, 5))

        self.canvas_setup_frame = ttk.Frame(self, borderwidth=2, relief="groove", padding=(10, 10, 10, 10))
        self.canvas_setup_frame.grid(row=2, column=2, rowspan=6)

        self.clear_canvas_button = ttk.Button(self.canvas_setup_frame, text="Clear canvas", command=self.clear_canvas)
        self.clear_canvas_button.grid(row=0, column=0, padx=(0, 5), pady=(0, 5))

        self.help_text = ttk.Label(self.canvas_setup_frame, text="Hold left key to move point\nRight click to create a point\nMiddle click to delete a point")
        self.help_text.grid(row=1, column=0, padx=(0, 5), pady=(0, 5))

        self.canvas_frame = ttk.Frame(self)
        self.canvas_frame.grid(row=0, column=0, rowspan=6)

        self.canvas = tk.Canvas(self.canvas_frame, width=800, height=800, bg="white")
        self.canvas.pack()

        self.canvas.bind("<Button-3>", self.on_mouse_click)
        self.canvas.bind("<ButtonPress-1>", self.on_mouse_hold_start)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_hold_end)
        self.canvas.bind("<Button-2>", self.delete_point_on_click)

        # self.draw_axes()

    def choose_point_color(self):
        color = colorchooser.askcolor(title="Choose point color")
        self.color_styles["points"] = color[1]
        self.color_frame.config(bg=self.color_styles["points"])
        self.update_control_points_color()

    def choose_curve_color(self):
        color = colorchooser.askcolor(title="Choose curve color")
        self.color_styles["curve"] = color[1]
        self.curve_color_frame.config(bg=self.color_styles["curve"])
        self.update_canvas()

    def choose_control_line_color(self):
        color = colorchooser.askcolor(title="Choose control line color")
        self.color_styles["control_line"] = color[1]
        self.control_line_color_frame.config(bg=self.color_styles["control_line"])
        self.update_canvas()

    def tabulate_window(self):
        def tabulate():
            ax.clear()
            try:
                step = float(step_entry.get())
                start = float(start_entry.get())
                end = float(end_entry.get())

                assert 0 <= start < end <= 1 and 0 < step <= end - start
                assert self.bezier_curve_line
            except AssertionError:
                messagebox.showerror("Error", "Invalid input")
                return
            except ValueError:
                messagebox.showerror("Error", "Invalid input")
                return

            x = []
            y = []

            while start < end:
                point = self.bezier_curve.get_curve_point(start)
                x_, y_ = self.canvas_to_cartesian(point[0], point[1])
                x.append(x_)
                y.append(y_)

                start += step

            ax.plot(x, y)
            canvas.draw()

        tabulate_window = tk.Toplevel(self)
        tabulate_window.title("Tabulate")
        tabulate_window.geometry("700x500")

        slider_frame = ttk.Frame(tabulate_window)
        slider_frame.grid(row=0, column=0, padx=(10, 10), pady=(10, 10))

        slider_label = ttk.Label(slider_frame, text="Step: ")
        slider_label.grid(row=0, column=0, padx=(25, 5))

        step_entry = ttk.Entry(slider_frame, width=15)
        step_entry.grid(row=0, column=1, padx=(5, 5))

        start_label = ttk.Label(slider_frame, text="Start: ")
        start_label.grid(row=0, column=2, padx=(5, 5))

        start_entry = ttk.Entry(slider_frame, width=15)
        start_entry.grid(row=0, column=3, padx=(5, 5))

        end_label = ttk.Label(slider_frame, text="End: ")
        end_label.grid(row=0, column=4, padx=(5, 5))

        end_entry = ttk.Entry(slider_frame, width=15)
        end_entry.grid(row=0, column=5, padx=(5, 5))

        tabulate_button = ttk.Button(slider_frame, text="Tabulate", command=tabulate)
        tabulate_button.grid(row=1, column=0, columnspan=7, pady=(10, 10))

        fig, ax = plt.subplots(figsize=(5, 2.5))

        # Create a FigureCanvasTkAgg to embed the Matplotlib plot into the Toplevel window
        canvas = FigureCanvasTkAgg(fig, master=tabulate_window)
        canvas.draw()

        # Pack the canvas into the Toplevel window
        canvas.get_tk_widget().grid(row=2, column=0, padx=(10, 10), pady=(10, 10), columnspan=7)

    def show_matrix_window(self):
        def show_matrix():
            try:
                top_left_index = (int(top_left_row_entry.get()), int(top_left_col_entry.get()))
                bottom_right_index = (int(bottom_right_row_entry.get()), int(bottom_right_col_entry.get()))
            except ValueError:
                matrix_text.delete('1.0', tk.END)
                matrix_text.insert('1.0', "Invalid indices")
                return

            try:
                if top_left_index[0] <= bottom_right_index[0] and top_left_index[1] <= bottom_right_index[1]:
                    # matrix_fragment = self.bezier_curve.get_coef_matrix()
                    matrix_fragment = self.bezier_curve.get_coef_matrix()[top_left_index[0]:bottom_right_index[0] + 1, top_left_index[1]:bottom_right_index[1] + 1]
                    matrix_text.delete('1.0', tk.END)
                    matrix_text.insert('1.0', str(matrix_fragment))
                else:
                    raise ValueError(
                        "Invalid indices. Bottom right index must be greater than or equal to top left index.")
            except Exception as e:
                matrix_text.delete('1.0', tk.END)
                matrix_text.insert('1.0', f"Error: {e}")

        # Create a numpy array as an example matrix

        matrix_window = tk.Toplevel(self)
        matrix_window.title("Matrix Fragment")
        matrix_window.geometry("500x500")

        # Create labels and entry widgets for top left and bottom right indices
        top_left_row_label = ttk.Label(matrix_window, text="Top Left Row:")
        top_left_row_label.grid(row=0, column=0, padx=5, pady=5)

        top_left_row_entry = ttk.Entry(matrix_window, width=5)
        top_left_row_entry.grid(row=0, column=1, padx=5, pady=5)

        top_left_col_label = ttk.Label(matrix_window, text="Top Left Column:")
        top_left_col_label.grid(row=0, column=2, padx=5, pady=5)

        top_left_col_entry = ttk.Entry(matrix_window, width=5)
        top_left_col_entry.grid(row=0, column=3, padx=5, pady=5)

        bottom_right_row_label = ttk.Label(matrix_window, text="Bottom Right Row:")
        bottom_right_row_label.grid(row=1, column=0, padx=5, pady=5)

        bottom_right_row_entry = ttk.Entry(matrix_window, width=5)
        bottom_right_row_entry.grid(row=1, column=1, padx=5, pady=5)

        bottom_right_col_label = ttk.Label(matrix_window, text="Bottom Right Column:")
        bottom_right_col_label.grid(row=1, column=2, padx=5, pady=5)

        bottom_right_col_entry = ttk.Entry(matrix_window, width=5)
        bottom_right_col_entry.grid(row=1, column=3, padx=5, pady=5)

        # Create a button to show the matrix fragment
        show_button = ttk.Button(matrix_window, text="Show Matrix", command=show_matrix)
        show_button.grid(row=2, columnspan=4, padx=5, pady=5)

        # Create a Text widget to display the matrix fragment
        matrix_text = tk.Text(matrix_window, width=40, height=10)
        matrix_text.grid(row=3, columnspan=4, padx=5, pady=5)

    def delete_point_on_click(self, event):
        point = self.identify_control_point(event.x, event.y)
        if point:
            index = self.control_points.index(point)
            self.bezier_curve.delete_control_point(index)
            self.control_points.remove(point)
            self.canvas.delete(point)
            self.update_canvas()

    def on_mouse_hold_start(self, event):
        active_point = self.identify_control_point(event.x, event.y)
        if active_point:
            self.on_mouse_hold(event, active_point)

    def on_mouse_hold(self, event, active_point):

        self.move_point(event, active_point)
        self.hold_event = self.after(1, self.on_mouse_hold, event, active_point)

    def get_mouse_position(self):
        x = self.canvas.winfo_pointerx() - self.canvas.winfo_rootx()
        y = self.canvas.winfo_pointery() - self.canvas.winfo_rooty()
        return x, y

    def move_point(self, event, active_point):
        x, y = self.get_mouse_position()
        circle = self.canvas.coords(active_point)
        point_x = (circle[0] + circle[2]) / 2
        point_y = (circle[1] + circle[3]) / 2
        self.canvas.move(active_point, x - point_x, y - point_y)
        self.update_control_point(self.control_points.index(active_point), x, y)

    def update_control_point(self, index, x, y):
        self.bezier_curve.set_control_point(index, x, y)
        # self.draw_beizer_curve()
        self.update_canvas()

    def on_mouse_hold_end(self, event):
        if self.hold_event:
            self.after_cancel(self.hold_event)

    def identify_control_point(self, x, y):
        for point in self.control_points:
            point_coords = self.canvas.coords(point)
            if abs(x - point_coords[0]) < 15 and abs(y - point_coords[1]) < 15:
                return point
        return None

    def on_mouse_click(self, event):
        # x, y = self.canvas_to_cartesian(event.x, event.y)
        x, y = event.x, event.y
        self.draw_control_point(x, y)
        self.bezier_curve.add_control_point(x, y)
        if self.bezier_curve_line:
            self.update_canvas()

    def update_canvas(self):
        curve = True if self.bezier_curve_line else False
        self.canvas.delete(self.bezier_curve_line)
        self.canvas.delete(self.bezier_curve_control_line)
        if self.bezier_curve.get_control_points().shape[0] >= 2 and curve:
            self.draw_beizer_curve()

    def update_control_points_color(self):
        for point in self.control_points:
            self.canvas.itemconfig(point, fill=self.color_styles["points"])

    def draw_control_point(self, x, y):
        self.control_points.append(self.canvas.create_oval(x - 8, y - 8, x + 8, y + 8, fill=self.color_styles["points"]))

    def draw_bezier_curve_action(self):
        try:
            assert self.bezier_curve.get_control_points().shape[0] >= 2
        except AssertionError:
            messagebox.showerror("Error", "At least 2 control points are required to draw a curve")
        else:
            self.draw_beizer_curve()

    def draw_beizer_curve(self):
        curve_points = self.bezier_curve.get_curve_points()
        self.draw_control_line()
        flattened_curve_points = curve_points.flatten()  # Reshape the array into a 1D array
        self.bezier_curve_line = self.canvas.create_line(*flattened_curve_points, fill=self.color_styles["curve"], width=4)

    def draw_control_line(self):
        control_points = self.bezier_curve.get_control_points()

        # for point in control_points:
        #     self.draw_control_point(point[0], point[1])
        flattened_control_points = control_points.flatten()  # Reshape the array into a 1D array
        self.bezier_curve_control_line = self.canvas.create_line(*flattened_control_points,
                                                                 fill=self.color_styles["control_line"], width=4)

    def canvas_to_cartesian(self, x, y):
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        cartesian_x = (x - canvas_width / 2) / (self.scale * 2)  # Adjust scale as needed
        cartesian_y = (canvas_height / 2 - y) / (self.scale * 2)  # Adjust scale as needed
        return cartesian_x, cartesian_y

    def clear_canvas(self):
        self.canvas.delete("all")
        self.bezier_curve.reset_curve()
        self.control_points = []
        self.bezier_curve_line = None
        self.bezier_curve_control_line = None
        # self.draw_axes()


if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
