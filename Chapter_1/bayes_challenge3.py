import sys
import random
import itertools
import numpy as np
import cv2 as cv

MAP_FILE = 'cape_python.png'

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
        self.psep1 = 0
        self.psep2 = 0
        self.psep3 = 0
        
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

    def calc_planned_search_effectiveness(self):
        """Set planned decimal search effectiveness value per search area."""        
        self.psep1 = random.uniform(0.2, 1 - self.tsep1)
        self.psep2 = random.uniform(0.2, 1 - self.tsep2)
        self.psep3 = random.uniform(0.2, 1 - self.tsep3)    


    def calc_search_effectiveness(self):
        """Set decimal search effectiveness value per search area.""" 
        self.sep1 = random.triangular(low=self.psep1 * 0.8,high=self.psep1 * 1.2)
        self.sep2 = random.triangular(low=self.psep2 * 0.8,high=self.psep2 * 1.2)
        self.sep3 = random.triangular(low=self.psep3 * 0.8,high=self.psep3 * 1.2)

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


    def draw_menu(self, search_num):
        """Print menu of choices for conducting area searches."""
        if search_num == 1:
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
        else:
            print("\nSearch {}".format(search_num))
            print(
            """
            Choose next areas to search:
    
            0 - Quit
            
            1 - Search Area 1 twice
              Probability of detection: {:.3f}
              
            2 - Search Area 2 twice
              Probability of detection: {:.3f}
              
            3 - Search Area 3 twice
              Probability of detection: {:.3f}
              
            4 - Search Areas 1 & 2
              Probability of detection: {:.3f}
              
            5 - Search Areas 1 & 3
              Probability of detection: {:.3f}
              
            6 - Search Areas 2 & 3
              Probability of detection: {:.3f}
              
            7 - Start Over
            
            Choice:
            """.format(1 - (1 - self.psep1 * self.p1)**2,
                       1 - (1 - self.psep2 * self.p2)**2,
                       1 - (1 - self.psep3 * self.p3)**2,
                       self.psep1 * self.p1 + self.psep2 * self.p2,
                       self.psep1 * self.p1 + self.psep3 * self.p3,
                       self.psep2 * self.p2 + self.psep3 * self.p3)
            )
            print("-" * 65)


def main():
    app = Search('Cape_Python')
    app.draw_map(last_known=(160, 290))
    sailor_x, sailor_y = app.sailor_final_location(num_search_areas=3)
    print("-" * 65)
    print("\nInitial Target (P) Probabilities:")
    print("P1 = {:.3f}, P2 = {:.3f}, P3 = {:.3f}".format(app.p1, app.p2, app.p3))
    print("Max Prob = {:.3f}".format(max(app.p1, app.p2, app.p3)))
    search_num = 1

    while True:
        app.calc_planned_search_effectiveness()
        app.calc_search_effectiveness()
        print("\nNew Planned Search Effectiveness and Target Probabilities" 
                  "(P) for Search {}:".format(search_num + 1))
        print("E1 = {:.3f}, E2 = {:.3f}, E3 = {:.3f}"
                  .format(app.psep1, app.psep2, app.psep3))
        print("P1 = {:.3f}, P2 = {:.3f}, P3 = {:.3f}"
                  .format(app.p1, app.p2, app.p3))
        app.draw_menu(search_num)
        choice = input("Choice: ")

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
            continue

        app.revise_target_probs()  # Use Bayes' rule to update target probs.

        print("\nSearch {} Results 1 = {}"
              .format(search_num, results_1), file=sys.stderr)
        print("Search {} Results 2 = {}\n"
              .format(search_num, results_2), file=sys.stderr)
        print("Actual Search {} Effectiveness (E):".format(search_num))
        print("E1 = {:.3f}, E2 = {:.3f}, E3 = {:.3f}"
              .format(app.sep1, app.sep2, app.sep3))
        print("Actual Cumulative Search {} Total Effectiveness (E):".format(search_num))
        print("E1 = {:.3f}, E2 = {:.3f}, E3 = {:.3f}"
              .format(app.tsep1, app.tsep2, app.tsep3))


        # Show position if sailor found, else continue
        if results_1 != 'Not Found' or results_2 != 'Not Found':
            cv.circle(app.img, (sailor_x, sailor_y), 3, (255, 0, 0), -1)
            cv.imshow('Search Area', app.img)
            cv.waitKey(1500)
            main()
            
        search_num += 1

if __name__ == '__main__':
    main()