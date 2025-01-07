""" © Daniel P Raven and Matt Russell 2024 All Rights Reserved """

from itertools import combinations, permutations
import statistics
import tkinter

import qtr_pairing_process.utility_funcs as uf

class TreeGenerator:
    def __init__(
        self,
        treeview,
        sort_alpha
    ):
        self.treeview = treeview
        self.sort_alpha = sort_alpha
        self.original_order = {}
        self.fRatings = None

    def generate_combinations(self, fNames, oNames, fRatings, oRatings):
        self.fRatings = fRatings
        self.treeview.tree.delete(*self.treeview.tree.get_children())
        tree_top = self.treeview.tree.insert("", 'end', text="Pairings")
        fNames_sorted = sorted(fNames, key=lambda x: x) if self.sort_alpha else fNames
        oNames_sorted = sorted(oNames, key=lambda x: x) if self.sort_alpha else oNames
        
        for name in fNames_sorted:
            fnames_filtered = [x for x in fNames_sorted if x!=name]

            # print(f"Top Level: {name} in {fNames_sorted}")
            self.generate_nested_combinations(name, fnames_filtered, oNames_sorted, fRatings, oRatings, tree_top)
            fNames_sorted[:] = uf.cycle_list(fNames_sorted)
            # oNames_sorted[:] = cycle_list(oNames_sorted)
        
    def generate_nested_combinations(self, first_fName, fNames, oNames, fRatings, oRatings, parent):
        
        combs = list(combinations(oNames, 2))
        if oNames and not combs:
            first_oName = oNames[0]
            combs = list(combinations([first_oName,first_oName], 2))
        combs_sorted = sorted(combs, key=lambda x: (x[0], x[1])) if self.sort_alpha else combs
        for comb in combs_sorted:
            rating_0 = fRatings[first_fName].get(comb[0], 'N/A')
            rating_1 = fRatings[first_fName].get(comb[1], 'N/A')
            item_id = self.treeview.tree.insert(parent, 'end', text=f"{first_fName} vs {comb[0]} ({rating_0}/5) OR {comb[1]} ({rating_1}/5)", values=max(rating_0, rating_1), tags=max(rating_0, rating_1))
            
            if fNames:
                opponent_perms = list(permutations(comb, 2))
                for opponent, next_fName in opponent_perms:                    
                    nested_oNames = [name for name in oNames if name != opponent and name!=next_fName]
                    nested_fNames = [name for name in fNames if name != first_fName]
                    child_id = self.treeview.tree.insert(item_id, 'end', text=f"{opponent} rating {fRatings[first_fName].get(opponent)}", values=fRatings[first_fName].get(opponent), tags=fRatings[first_fName].get(opponent))                    
                    self.generate_nested_combinations(next_fName,nested_oNames, fNames, oRatings, fRatings, child_id)

    def set_value(self,value, node):
        try:
            self.treeview.tree.set(node,'Rating',value)
        except (ValueError, IndexError):
            print(f"set_item_details has failed")
            return 0

    def traverse_and_sum_values(self, mode=0):
        # Get all root nodes
        print(f"MODE = {mode}")
        root_nodes = self.treeview.tree.get_children()
        for root in root_nodes:
            self.sum_leaf_values(root,mode)

    def sum_leaf_values(self, node, mode=0):
        child_ids = self.treeview.tree.get_children(node)
        
        # If this is a Leaf node, return the integer value from the values column
        if not child_ids:
            try:
                value = int(self.treeview.tree.item(node, 'values')[0])
                return value
            except (ValueError, IndexError) as e:
                print(f"sum_leaf_values error: {e}")
                return 0
        
        # This is a branch node, continue recursion
        total_sum = 0
        match_ratings = []

        for child_id in child_ids:
            current_value = self.sum_leaf_values(child_id, mode)
            total_sum += current_value
            match_ratings.append(current_value)
        
        # Set node value based on mode
        if mode == 0:       # Maximize Matchup Strength!
            max_rating = max(match_ratings)
            self.set_value(max_rating, node)
        elif mode == 1:     # Sum Matchup Strength! - Full sum of all nodes all the way up the tree.
                            # Sum the values of child nodes
            self.set_value(total_sum, node)
        elif mode == 2:     # "MIN" matchup stength.
                            # Avoid Poor Matchups! This should be a risk averse sorting algorithm
            low_rating = min(match_ratings)
            self.set_value(low_rating, node)
        elif mode == 3:     # "AVG" Matchup strength.
            avg_rating = statistics.mean(match_ratings)
            self.set_value(avg_rating, node)
        
        return total_sum
    
    def sort_matchup_value(self):
        self.save_original_order()
        root_nodes = self.treeview.tree.get_children()
        for root in root_nodes:
            self.sort_children(root)
    
    # NEW SORTING LOGIC - CALCULATE_FLOOR???
    def sort_children(self, node):
        child_ids = self.treeview.tree.get_children(node)
        if child_ids:
            children_with_scores = []
            for child_id in child_ids:
                value = int(self.treeview.tree.item(child_id, 'values')[0])
                siblings = [int(self.treeview.tree.item(sibling_id, 'values')[0]) for sibling_id in child_ids if sibling_id != child_id]
                # Calculate the floor for each player against the enemy team
                floor_score = self.calculate_floor(child_id, siblings)
                children_with_scores.append((child_id, floor_score))
            
            children_with_scores.sort(key=lambda x: x[1], reverse=True)
            sorted_child_ids = [child_id for child_id, score in children_with_scores]

            for child_id in child_ids:
                self.treeview.tree.detach(child_id)
            for child_id in sorted_child_ids:
                self.treeview.tree.move(child_id, node, 'end')

            # Recursively sort the children of each child
            for child_id in sorted_child_ids:
                self.sort_children(child_id)

    def calculate_floor(self, node, siblings):
        # Assuming fRatings is a class attribute or passed appropriately
        fRatings = self.treeview.tree.item(node, 'values')[0]
        oNames = [sibling for sibling in siblings]
        floor_score = sum(int(fRatings) for opponent in oNames)
        return floor_score
    
    # NEW SORT - PROPOSAL CONCEPT - closeness to 3.
    # def sort_children(self, node):
    #     child_ids = self.treeview.tree.get_children(node)
    #     if child_ids:
    #         children_with_scores = []
    #         for child_id in child_ids:
    #             value = int(self.treeview.tree.item(child_id, 'values')[0])
    #             siblings = [int(self.treeview.tree.item(sibling_id, 'values')[0]) for sibling_id in child_ids if sibling_id != child_id]
    #             # calculate_score should take into account the factors for wtc level pairings
    #             score = self.calculate_score(value, siblings)
    #             children_with_scores.append((child_id, score))
            
    #         children_with_scores.sort(key=lambda x: x[1], reverse=True)
    #         sorted_child_ids = [child_id for child_id, score in children_with_scores]

    #         for child_id in child_ids:
    #             self.treeview.tree.detach(child_id)
    #         for child_id in sorted_child_ids:
    #             self.treeview.tree.move(child_id, node, 'end')

    #         # Recursively sort the children of each child
    #         for child_id in sorted_child_ids:
    #             self.sort_children(child_id)

    def calculate_score(self, value, siblings):
        closeness_to_3 = sum(abs(sibling - 3) for sibling in siblings) / len(siblings) if siblings else 0
        return (5 - closeness_to_3) + value

    def save_original_order(self):
        # Save the original order of the children for each root node
        root_nodes = self.treeview.tree.get_children()
        for root in root_nodes:
            child_ids = self.treeview.tree.get_children(root)
            self.original_order[root] = list(child_ids)


    def unsort_matchup_tree(self):
        # Restore the original order of the children for each root node
        for root, original_child_ids in self.original_order.items():
            try:
                # Get the current child nodes
                current_child_ids = self.treeview.tree.get_children(root)
            except tkinter.TclError as e:
                print(f"Error getting children of root {root}: {e}")
                continue
            
            # Detach all current children
            for child_id in current_child_ids:
                try:
                    self.treeview.tree.detach(child_id)
                except tkinter.TclError as e:
                    print(f"Error detaching child {child_id}: {e}")
                    continue
            
            # Reinsert the children in their original order
            for child_id in original_child_ids:
                try:
                    self.treeview.tree.move(child_id, root, 'end')
                except tkinter.TclError as e:
                    print(f"Error moving child {child_id} to root {root}: {e}")