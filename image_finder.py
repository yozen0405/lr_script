import cv2

def find_template_position(screen_path, template_path, threshold=0.8, region=None):
    screen = cv2.imread(screen_path)
    template = cv2.imread(template_path)

    if screen is None or template is None:
        return None

    if region:
        x1, y1, x2, y2 = region
        screen = screen[y1:y2, x1:x2]
        # cv2.imwrite("debug_region_screen.png", screen)

    res = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(res)
    # print(max_val)

    if max_val >= threshold:
        h, w = template.shape[:2]
        offset_x, offset_y = (region[0], region[1]) if region else (0, 0)
        return (max_loc[0] + w // 2 + offset_x, max_loc[1] + h // 2 + offset_y)
    else:
        return None
