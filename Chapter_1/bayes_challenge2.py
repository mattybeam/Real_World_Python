import sys
import random
import itertools
import numpy as np
import cv2 as cv

MAP_FILE = 'cape_python.png'
VALID_STRATEGY = {0, 1}

# Assign search area (SA) corner point locations based on image pixels.
SA1_CORNERS = (130, 265, 180, 315)  # (UL-X, UL-Y, LR-X, LR-Y)
SA2_CORNERS = (80, 255, 130, 305)   # (UL-X, UL-Y, LR-X, LR-Y)
SA3_CORNERS = (105, 205, 155, 255)  # (UL-X, UL-Y, LR-X, LR-Y)


class Search():
    """Bayesian Search & Rescue game with 3 search areas."""

    def __init__(self, name):
        self.name = name
        self.img = cv.imread(MAP_FILE, cv.IMREAD_COLOR)
        if self.img is None:
            print('Could not load map file {}'.format(MAP_FILE),
                  file = sys.stderr)
            sys.exit(1)

        # Set placeholders for sailor's actual location
        self.area_actual = 0
        self.sailor_actual = [0, 0]  # As "local" coords within search area

        # Create numpy arrays for each search area by indexing image array.
        self.sa1 = self.img[SA1_CORNERS[1] : SA1_CORNERS[3],
                            SA1_CORNERS[0] : SA1_CORNERS[2]]

        self.sa2 = self.img[SA2_CORNERS[1] : SA2_CORNERS[3],
                            SA2_CORNERS[0] : SA2_CORNERS[2]]

        self.sa3 = self.img[SA3_CORNERS[1] : SA3_CORNERS[3], 
                            SA3_CORNERS[0] : SA3_CORNERS[2]]
        
        # Create empty lists for search area that has been searched.
        self.ssa1 = []
        self.ssa2 = []
        self.ssa3 = []

        # Set initial per-area target probabilities for finding sailor
        self.p1 = 0.2
        self.p2 = 0.5
        self.p3 = 0.3

        # Initialize search effectiveness probabilities.
        self.sep1 = 0
        self.sep2 = 0
        self.sep3 = 0
        
        self.tsep1 = 0
        self.tsep2 = 0
        self.tsep3 = 0
        

    def draw_map(self, last_known):
        """Display basemap with scale, last known xy location, search areas."""
        # Draw the scale bar.
        cv.line(self.img, (20, 370), (70, 370), (0, 0, 0), 2)
        cv.putText(self.img, '0', (8, 370), cv.FONT_HERSHEY_PLAIN, 1, (0, 0, 0))
        cv.putText(self.img, '50 Nautical Miles', (71, 370),
                   cv.FONT_HERSHEY_PLAIN, 1, (0, 0, 0))

        # Draw and number the search areas.
        cv.rectangle(self.img, (SA1_CORNERS[0], SA1_CORNERS[1]),
                     (SA1_CORNERS[2], SA1_CORNERS[3]), (0, 0, 0), 1)
        cv.putText(self.img, '1',
                   (SA1_CORNERS[0] + 3, SA1_CORNERS[1] + 15),
                   cv.FONT_HERSHEY_PLAIN, 1, 0)
        cv.rectangle(self.img, (SA2_CORNERS[0], SA2_CORNERS[1]),
                     (SA2_CORNERS[2], SA2_CORNERS[3]), (0, 0, 0), 1)
        cv.putText(self.img, '2',
                   (SA2_CORNERS[0] + 3, SA2_CORNERS[1] + 15),
                   cv.FONT_HERSHEY_PLAIN, 1, 0)
        cv.rectangle(self.img, (SA3_CORNERS[0], SA3_CORNERS[1]),
                     (SA3_CORNERS[2], SA3_CORNERS[3]), (0, 0, 0), 1)
        cv.putText(self.img, '3',
                   (SA3_CORNERS[0] + 3, SA3_CORNERS[1] + 15),
                   cv.FONT_HERSHEY_PLAIN, 1, 0)

        # Post the last known location of the sailor.
        cv.putText(self.img, '+', (last_known),
                   cv.FONT_HERSHEY_PLAIN, 1, (0, 0, 255))
        cv.putText(self.img, '+ = Last Known Position', (274, 355),
                   cv.FONT_HERSHEY_PLAIN, 1, (0, 0, 255))
        cv.putText(self.img, '* = Actual Position', (275, 370),
                   cv.FONT_HERSHEY_PLAIN, 1, (255, 0, 0))

        cv.imshow('Search Area', self.img)
        cv.moveWindow('Search Area', 750, 10)
        cv.waitKey(500)

    def sailor_final_location(self, num_search_areas):
        """Return the actual x,y location of the missing sailor."""
        # Find sailor coordinates with respect to any Search Area sub-array.
        self.sailor_actual[0] = np.random.choice(self.sa1.shape[1])
        self.sailor_actual[1] = np.random.choice(self.sa1.shape[0])

        # Pick a search area at random.
        area = int(random.triangular(1, num_search_areas + 1))

        # Convert local search area coordinates to map coordinates.
        if area == 1:
            x = self.sailor_actual[0] + SA1_CORNERS[0]
            y = self.sailor_actual[1] + SA1_CORNERS[1]
            self.area_actual = 1
        elif area == 2:
            x = self.sailor_actual[0] + SA2_CORNERS[0]
            y = self.sailor_actual[1] + SA2_CORNERS[1]
            self.area_actual = 2
        else:
            x = self.sailor_actual[0] + SA3_CORNERS[0]
            y = self.sailor_actual[1] + SA3_CORNERS[1]
            self.area_actual = 3
        return x, y

    def calc_search_effectiveness(self):
        """Set decimal search effectiveness value per search area."""
        self.sep1 = random.uniform(0.2, 0.9)
        self.sep2 = random.uniform(0.2, 0.9)
        self.sep3 = random.uniform(0.2, 0.9)

    def conduct_search(self, area_num, area_array, effectiveness_prob):
        """Return search results and list of searched coordinates."""
        local_y_range = range(area_array.shape[0])
        local_x_range = range(area_array.shape[1])        
        if area_num == 1:
            coords = list(set(itertools.product(local_x_range, local_y_range))\
                     - set(self.ssa1))
            random.shuffle(coords)
            coords = coords[:int((len(coords) * effectiveness_prob))]
            self.ssa1 = self.ssa1 + coords
            self.tsep1 = len(self.ssa1) / len(list(itertools.product(local_x_range, local_y_range)))
        elif area_num == 2:
            coords = list(set(itertools.product(local_x_range, local_y_range)) - \
                    set(self.ssa2))
            random.shuffle(coords)
            coords = coords[:int((len(coords) * effectiveness_prob))]
            self.ssa2 = self.ssa2 + coords
            self.tsep2 = len(self.ssa2) / len(list(itertools.product(local_x_range, local_y_range)))
        else:
            coords = list(set(itertools.product(local_x_range, local_y_range)) - \
                    set(self.ssa3))
            random.shuffle(coords)
            coords = coords[:int((len(coords) * effectiveness_prob))]
            self.ssa3 = self.ssa3 + coords
            self.tsep3 = len(self.ssa3) / len(list(itertools.product(local_x_range, local_y_range)))
        loc_actual = (self.sailor_actual[0], self.sailor_actual[1])
        if area_num == self.area_actual and loc_actual in coords:
            return 'Found in Area {}.'.format(area_num), coords
        return 'Not Found', coords

    def revise_target_probs(self):
        """Update area target probabilities based on search effectiveness."""
        denom = self.p1 * (1 - self.sep1) + self.p2 * (1 - self.sep2) \
                + self.p3 * (1 - self.sep3)
        self.p1 = self.p1 * (1 - self.sep1) / denom
        self.p2 = self.p2 * (1 - self.sep2) / denom
        self.p3 = self.p3 * (1 - self.sep3) / denom


def draw_menu(search_num):
    """Print menu of choices for conducting area searches."""
    print('\nSearch {}'.format(search_num))
    print(
        """
        Choose next areas to search:

        0 - Quit
        1 - Search Area 1 twice
        2 - Search Area 2 twice
        3 - Search Area 3 twice
        4 - Search Areas 1 & 2
        5 - Search Areas 1 & 3
        6 - Search Areas 2 & 3
        7 - Start Over
        """
        )


def main():
    app = Search('Cape_Python')
    sailor_x, sailor_y = app.sailor_final_location(num_search_areas=3)
    search_num = 1
    while search_num <= 3: # Limit to three days of searches
        app.calc_search_effectiveness()
        # if max(app.p1,app.p2,app.p3) == app.p1:
        #     choice = "1" 
        # elif max(app.p1,app.p2,app.p3) == app.p2:
        #     choice = "2"
        # else:
        #     choice = "3"
        
        if max(app.p1 + app.p2,app.p1 + app.p3,app.p2 + app.p3) == (app.p1 + app.p2):
            choice = "4" 
        elif max(app.p1 + app.p2,app.p1 + app.p3,app.p2 + app.p3) == (app.p1 + app.p3):
            choice = "5"
        else:
            choice = "6"
        
        if choice == "0":
            sys.exit()

        elif choice == "1":
            results_1, coords_1 = app.conduct_search(1, app.sa1, app.sep1)
            results_2, coords_2 = app.conduct_search(1, app.sa1, app.sep1)
            app.sep1 = (len(set(coords_1 + coords_2))) / (len(app.sa1)**2)
            app.sep2 = 0
            app.sep3 = 0

        elif choice == "2":
            results_1, coords_1 = app.conduct_search(2, app.sa2, app.sep2)
            results_2, coords_2 = app.conduct_search(2, app.sa2, app.sep2)
            app.sep1 = 0
            app.sep2 = (len(set(coords_1 + coords_2))) / (len(app.sa2)**2)
            app.sep3 = 0

        elif choice == "3":
            results_1, coords_1 = app.conduct_search(3, app.sa3, app.sep3)
            results_2, coords_2 = app.conduct_search(3, app.sa3, app.sep3)
            app.sep1 = 0
            app.sep2 = 0
            app.sep3 = (len(set(coords_1 + coords_2))) / (len(app.sa3)**2)

        elif choice == "4":
            results_1, coords_1 = app.conduct_search(1, app.sa1, app.sep1)
            results_2, coords_2 = app.conduct_search(2, app.sa2, app.sep2)
            app.sep3 = 0

        elif choice == "5":
            results_1, coords_1 = app.conduct_search(1, app.sa1, app.sep1)
            results_2, coords_2 = app.conduct_search(3, app.sa3, app.sep3)
            app.sep2 = 0

        elif choice == "6":
            results_1, coords_1 = app.conduct_search(2, app.sa2, app.sep2)
            results_2, coords_2 = app.conduct_search(3, app.sa3, app.sep3)
            app.sep1 = 0

        elif choice == "7":
            main()

        else:
            print("\nSorry, but that isn't a valid choice.", file=sys.stderr)
            print("Choice = {}".format(choice))
            continue

        app.revise_target_probs()  # Use Bayes' rule to update target probs.


        # If sailor is found, return search number and restart
        if results_1 != 'Not Found' or results_2 != 'Not Found':
            return search_num
            main()
        search_num += 1
    

if __name__ == '__main__':
    search_success = []
    while len(search_success)<10000:
        search_success.append(main())
    no_success = sum(x is None for x in search_success)
    no_success_rate = no_success / 10000
    rev_search_success = [x for x in search_success if x] # Remove None values
    avg_success = sum(rev_search_success) / len(rev_search_success)
    print(search_success)
    print("Total unsuccessful searches: {}".format(no_success))
    print("No success rate: {:.3f}".format(no_success_rate))
    print("Success rate: {:.3f}".format(1-no_success_rate))
    print("\nAverage success: {:.3f}".format(avg_success))
