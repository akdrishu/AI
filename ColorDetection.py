import cv2

class Camera:
    def __init__(self):
        self.cam = cv2.VideoCapture(0)
        self.main_cube_coordinates = [
            [200, 120], [300, 120], [400, 120],
            [200, 220], [300, 220], [400, 220],
            [200, 320], [300, 320], [400, 320]
        ]

        self.current_cube_coordinates = [
            [20, 20], [54, 20], [88, 20],
            [20, 54], [54, 54], [88, 54],
            [20, 88], [54, 88], [88, 88]
        ]

        self.preview_cube_coordinates = [
            [20, 130], [54, 130], [88, 130],
            [20, 164], [54, 164], [88, 164],
            [20, 198], [54, 198], [88, 198]
        ]

    def name_to_rgb(self, name):
        color = {
            'red': (0, 0, 255),
            'orange': (0, 165, 255),
            'blue': (255, 0, 0),
            'green': (0, 255, 0),
            'white': (255, 255, 255),
            'yellow': (0, 255, 255)
        }
        return color[name]

    def hsv_to_name(self, hsv):
        h, s, v = hsv
        #print(hsv)
        if h < 15 and v < 100:
            return 'red'
        if h <= 10 and v > 100:
            return 'orange'
        elif h <= 30 and s <= 100:
            return 'white'
        elif h <= 40:
            return 'yellow'
        elif h <= 85:
            return 'green'
        elif h <= 130:
            return 'blue'

        return 'white'

    def average_hsv(self, roi):
        h = 0
        s = 0
        v = 0
        num = 0
        for y in range(len(roi)):
            if y % 10 == 0:
                for x in range(len(roi[y])):
                    if x % 10 == 0:
                        hsv = roi[y][x]
                        num += 1
                        h += hsv[0]
                        s += hsv[1]
                        v += hsv[2]
        h /= num
        s /= num
        v /= num
        return int(h), int(s), int(v)

    def draw_main_cube(self, frame):
        for x, y in self.main_cube_coordinates:
            cv2.rectangle(frame, (x, y), (x + 30, y + 30), (255, 255, 255), 2)

    def draw_current_cube(self, frame, state):
        for index, (x, y) in enumerate(self.current_cube_coordinates):
            cv2.rectangle(frame, (x, y), (x + 32, y + 32), self.name_to_rgb(state[index]), -1)

    def draw_preview_cube(self, frame, state):
        for index, (x, y) in enumerate(self.preview_cube_coordinates):
            cv2.rectangle(frame, (x, y), (x + 32, y + 32), self.name_to_rgb(state[index]), -1)

    def color_to_notation(self, color):
        notation = {
            'green': 'F',
            'white': 'U',
            'blue': 'B',
            'red': 'R',
            'orange': 'L',
            'yellow': 'D'
        }
        return notation[color]

    def scan(self):
        sides = {}
        preview = ['white', 'white', 'white',
                   'white', 'white', 'white',
                   'white', 'white', 'white']
        state = [0, 0, 0,
                 0, 0, 0,
                 0, 0, 0]
        while True:
            _, frame = self.cam.read()
            frame = cv2.flip(frame,1)
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            key = cv2.waitKey(10) & 0xff

            self.draw_main_cube(frame)
            self.draw_preview_cube(frame, preview)

            for index, (x, y) in enumerate(self.main_cube_coordinates):
                roi = hsv[y:y + 32, x:x + 32]
                avg_hsv = self.average_hsv(roi)
                color_name = self.hsv_to_name(avg_hsv)
                state[index] = color_name

            self.draw_current_cube(frame, state)

            if key == 32:
                preview = list(state)
                self.draw_preview_cube(frame, state)
                face = self.color_to_notation(state[4])
                notation = [self.color_to_notation(color) for color in state]
                if face not in sides:
                    sides[face] = notation
                else:
                    print("You have done some mistake in scanning the sides. Try again")
                    exit()

                if len(sides) == 6:
                    break

            text = 'Scanned sides: {}/6'.format(len(sides))
            cv2.putText(frame, text, (20, 460), cv2.FONT_HERSHEY_TRIPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)

            if key == 27:
                break

            cv2.imshow("Rubix Cube", frame)

        self.cam.release()
        cv2.destroyAllWindows()
        if len(sides) == 6:
            return sides
        else:
            print("Sorry, you did not scan all 6 sides. Try again")
            exit()


if __name__ == "__main__":
    camera = Camera()
    camera.scan()
