import math

class LockerTowerConfigurator:
    def __init__(self):
        self.width = 18
        self.depth = 18
        self.height_options = [36, 48, 60, 72]
        self.control_housing_height = 18
        self.min_lockers = 1
        self.max_lockers = 24
        self.gap_between_towers = 0.5
        self.locker_height_options = [6, 12, 18, 24, 36, 48, 60, 72]
        self.lock_controller_options = {"Top": 4.0, "Bottom": 4.0, "Both": 8.0}
        self.lock_options = {"Basic": 5.00, "Medium": 50.00, "Premier": 85.00}
        self.hinge_options = {"Standard": 7.50, "Reinforced": 15.00}
        self.labor_rate = 50.00
        self.cnc_cost = 300.00
        self.markup_percentage = 1.5
        # Material costs: {material: {thickness (inches): cost per sqft}}
        self.materials = {
            "MDF": {0.75: 8.00, 1.0: 10.00},
            "Polywood": {0.75: 10.00, 1.0: 12.00},
            "Polygood": {0.75: 12.00, 1.0: 15.00}
        }
        self.thickness_tower = 0.75  # Frame, housing, controller
        self.thickness_door = 1.0    # Locker fronts, housing door
        self.third_party_hinges = False
        self.third_party_locks = False
        self.third_party_material = False
        self.third_party_labor = False
        self.third_party_cnc = False

    def calculate_locker_dimensions(self, locker_configs, base_tower_height, include_control_housing, lock_controller_location):
        total_lockers = sum(config["num_lockers"] for config in locker_configs)
        if not (self.min_lockers <= total_lockers <= self.max_lockers):
            raise ValueError(f"Total lockers must be between {self.min_lockers} and {self.max_lockers}.")
        if base_tower_height not in self.height_options:
            raise ValueError(f"Base tower height must be one of {self.height_options}.")
        if lock_controller_location not in self.lock_controller_options:
            raise ValueError(f"Lock controller must be one of {list(self.lock_controller_options.keys())}.")

        controller_height = self.lock_controller_options[lock_controller_location]
        adjusted_tower_height = base_tower_height + controller_height
        effective_height = adjusted_tower_height - controller_height
        if include_control_housing:
            effective_height -= self.control_housing_height

        total_locker_height = 0
        for config in locker_configs:
            num_lockers = config["num_lockers"]
            locker_heights = config["heights"]
            use_9_inch = config["use_9_inch"]
            if use_9_inch and (num_lockers % 2 != 0 or num_lockers < 2):
                raise ValueError("9-inch lockers must be even and ≥2.")
            if len(locker_heights) != (num_lockers // 2 if use_9_inch else num_lockers):
                raise ValueError(f"Expected {num_lockers // 2 if use_9_inch else num_lockers} heights.")
            for height in locker_heights:
                if height not in self.locker_height_options:
                    raise ValueError(f"Locker height must be one of {self.locker_height_options}.")
            total_locker_height += sum(locker_heights) * (1 if use_9_inch else 1)

        if total_locker_height != effective_height:
            raise ValueError(f"Total locker height ({total_locker_height}\") must equal {effective_height}\".")

        return (
            locker_configs,
            self.depth,
            self.width if include_control_housing else 0,
            self.control_housing_height,
            self.depth if include_control_housing else 0,
            adjusted_tower_height,
            controller_height
        )

    def calculate_surface_area(
        self, locker_configs, locker_depth, control_housing_width, control_housing_height,
        control_housing_depth, include_control_housing, lock_controller_location, controller_height
    ):
        # Initialize surface areas
        tower_surface_area = 0.0  # 0.75" thick (frame, housing, controller)
        door_surface_area = 0.0   # 1.0" thick (locker fronts, housing door)

        # Locker components
        for config in locker_configs:
            num_lockers = config["num_lockers"]
            locker_heights = config["heights"]
            use_9_inch = config["use_9_inch"]
            locker_width = 9 if use_9_inch else 18
            num_columns = 2 if use_9_inch else 1
            for height in locker_heights:
                # Tower (0.75"): sides, top, bottom
                sides = 2 * (locker_width * height) / 144  # Left/right
                top_bottom = 2 * (locker_width * locker_depth) / 144
                tower_surface_area += (sides + top_bottom) * num_columns
                # Door (1"): front only
                front = (locker_width * height) / 144
                door_surface_area += front * num_columns
            if num_columns == 2:
                # Subtract shared middle wall (0.75")
                tower_surface_area -= sum(height * locker_depth / 144 for height in locker_heights)

        # Control housing
        if include_control_housing:
            # Tower (0.75"): sides, top, bottom
            ch_sides = 2 * (control_housing_width * control_housing_height) / 144
            ch_top_bottom = 2 * (control_housing_width * control_housing_depth) / 144
            tower_surface_area += ch_sides + ch_top_bottom
            # Door (1"): front door
            ch_door = (control_housing_width * control_housing_height) / 144
            door_surface_area += ch_door

        # Lock controller
        controller_width = self.width
        controller_depth = self.depth
        if lock_controller_location in ["Top", "Bottom"]:
            # Tower (0.75"): sides, top, bottom
            lc_sides = 2 * (controller_width * controller_height) / 144
            lc_top_bottom = 2 * (controller_width * controller_depth) / 144
            tower_surface_area += lc_sides + lc_top_bottom
        elif lock_controller_location == "Both":
            # Two panels (0.75")
            lc_sides = 2 * (controller_width * 4.0) / 144
            lc_top_bottom = 2 * (controller_width * controller_depth) / 144
            tower_surface_area += 2 * (lc_sides + lc_top_bottom)

        # Frame
        max_height = max(sum(config["heights"]) for config in locker_configs)
        frame_height = max(max_height, control_housing_height if include_control_housing else 0)
        # Tower (0.75"): sides, top, bottom
        frame_sides = 2 * (self.width * frame_height) / 144
        frame_top_bottom = 2 * (self.width * self.depth) / 144
        tower_surface_area += frame_sides + frame_top_bottom

        if tower_surface_area < 0 or door_surface_area < 0:
            raise ValueError("Negative surface area.")

        return tower_surface_area, door_surface_area

    def calculate_hardware(self, locker_configs, include_control_housing, lock_type, hinge_type):
        num_lockers = sum(config["num_lockers"] for config in locker_configs)
        num_hinges = num_lockers * 2 + (2 if include_control_housing else 0)
        num_locks = num_lockers + (1 if include_control_housing else 0)
        hinge_total = 0.0 if self.third_party_hinges else num_hinges * self.hinge_options[hinge_type]
        lock_total = 0.0 if self.third_party_locks else num_locks * self.lock_options[lock_type]
        return hinge_total, lock_total

    def calculate_labor(self, locker_configs, include_control_housing):
        if self.third_party_labor:
            return 0.0
        base_hours = sum(config["num_lockers"] for config in locker_configs) * 1.0
        if include_control_housing:
            base_hours += 2.0
        additional_hours = sum(config["num_lockers"] * 0.5 for config in locker_configs if config["use_9_inch"])
        return (base_hours + additional_hours) * self.labor_rate

    def configure_tower(self, locker_configs, base_tower_height, include_control_housing, material, lock_type, hinge_type, lock_controller_location, num_towers):
        try:
            if material not in self.materials:
                raise ValueError(f"Material must be one of {list(self.materials.keys())}.")
            if lock_type not in self.lock_options:
                raise ValueError(f"Lock type must be one of {list(self.lock_options.keys())}.")
            if hinge_type not in self.hinge_options:
                raise ValueError(f"Hinge type must be one of {list(self.hinge_options.keys())}.")
            if lock_controller_location not in self.lock_controller_options:
                raise ValueError(f"Lock controller must be one of {list(self.lock_controller_options.keys())}.")

            (
                locker_configs, locker_depth, control_housing_width, control_housing_height,
                control_housing_depth, adjusted_tower_height, controller_height
            ) = self.calculate_locker_dimensions(locker_configs, base_tower_height, include_control_housing, lock_controller_location)

            tower_surface_area, door_surface_area = self.calculate_surface_area(
                locker_configs, locker_depth, control_housing_width, control_housing_height,
                control_housing_depth, include_control_housing, lock_controller_location, controller_height
            )

            # Bill of Materials
            bom = {
                "material": material,
                "tower_sqft": round(tower_surface_area, 2),  # 0.75"
                "door_sqft": round(door_surface_area, 2)     # 1"
            }

            # Material cost
            material_cost = 0.0 if self.third_party_material else (
                tower_surface_area * self.materials[material][self.thickness_tower] +
                door_surface_area * self.materials[material][self.thickness_door]
            )

            hinge_cost, lock_cost = self.calculate_hardware(locker_configs, include_control_housing, lock_type, hinge_type)
            hardware_cost = hinge_cost + lock_cost
            labor_cost = self.calculate_labor(locker_configs, include_control_housing)
            cnc_cost = 0.0 if self.third_party_cnc else self.cnc_cost / num_towers
            total_cost = material_cost + hardware_cost + labor_cost + cnc_cost
            sale_price = total_cost * self.markup_percentage

            return {
                "Base Tower Height (in)": base_tower_height,
                "Adjusted Tower Height (in)": adjusted_tower_height,
                "Number of Lockers": sum(config["num_lockers"] for config in locker_configs),
                "Control Housing": "Yes" if include_control_housing else "No",
                "Lock Controller Location": lock_controller_location,
                "Locker Configurations": [
                    {
                        "Width (in)": 9 if config["use_9_inch"] else 18,
                        "Number of Lockers": config["num_lockers"],
                        "Heights (in)": ", ".join(str(h) for h in config["heights"])
                    } for config in locker_configs
                ],
                "Material": material,
                "Lock Type": lock_type,
                "Hinge Type": hinge_type,
                "Bill of Materials": bom,
                "Material Cost ($)": round(material_cost, 2),
                "Hinge Cost ($)": round(hinge_cost, 2),
                "Lock Cost ($)": round(lock_cost, 2),
                "Hardware Cost ($)": round(hardware_cost, 2),
                "Labor Cost ($)": round(labor_cost, 2),
                "CNC Cutting Cost ($)": round(cnc_cost, 2),
                "Total Cost ($)": round(total_cost, 2),
                "Sale Price ($)": round(sale_price, 2)
            }
        except ValueError as e:
            return {"Error": str(e)}

    def configure_project(self, tower_configs):
        project_summary = []
        totals = {
            "material_cost": 0, "hinge_cost": 0, "lock_cost": 0,
            "hardware_cost": 0, "labor_cost": 0, "cnc_cost": 0,
            "total_cost": 0, "sale_price": 0
        }
        bom_totals = {}  # {material: {thickness: sqft}}
        x_position = 0
        num_towers = len(tower_configs)

        for i, config in enumerate(tower_configs, 1):
            tower_summary = self.configure_tower(
                config["locker_configs"], config["base_tower_height"], config["include_control_housing"],
                config["material"], config["lock_type"], config["hinge_type"],
                config["lock_controller_location"], num_towers
            )
            if "Error" in tower_summary:
                return {"Error": f"Tower {i}: {tower_summary['Error']}"}

            tower_summary["X Position Start (in)"] = round(x_position, 2)
            x_position += self.width + self.gap_between_towers
            tower_summary["X Position End (in)"] = round(x_position - self.gap_between_towers, 2)

            # Update BOM totals
            bom = tower_summary["Bill of Materials"]
            material = bom["material"]
            if material not in bom_totals:
                bom_totals[material] = {0.75: 0.0, 1.0: 0.0}
            bom_totals[material][0.75] += bom["tower_sqft"]
            bom_totals[material][1.0] += bom["door_sqft"]

            project_summary.append({f"Tower {i}": tower_summary})
            totals["material_cost"] += tower_summary["Material Cost ($)"]
            totals["hinge_cost"] += tower_summary["Hinge Cost ($)"]
            totals["lock_cost"] += tower_summary["Lock Cost ($)"]
            totals["hardware_cost"] += tower_summary["Hardware Cost ($)"]
            totals["labor_cost"] += tower_summary["Labor Cost ($)"]
            totals["cnc_cost"] += tower_summary["CNC Cutting Cost ($)"]
            totals["total_cost"] += tower_summary["Total Cost ($)"]
            totals["sale_price"] += tower_summary["Sale Price ($)"]

        project_totals = {
            "Bill of Materials": bom_totals,
            "Financial Summary": {
                "Total Material Cost ($)": round(totals["material_cost"], 2),
                "Total Hinge Cost ($)": round(totals["hinge_cost"], 2),
                "Total Lock Cost ($)": round(totals["lock_cost"], 2),
                "Total Hardware Cost ($)": round(totals["hardware_cost"], 2),
                "Total Labor Cost ($)": round(totals["labor_cost"], 2),
                "Total CNC Cutting Cost ($)": round(totals["cnc_cost"], 2),
                "Total Cost ($)": round(totals["total_cost"], 2),
                "Total Sale Price ($)": round(totals["sale_price"], 2),
                "Total Width (in)": round(x_position - self.gap_between_towers, 2)
            }
        }
        return {"Towers": project_summary, "Project Totals": project_totals}

    def display_summary(self, project_summary):
        print("\nLocker Tower Project Summary:")
        print("=" * 50)
        if "Error" in project_summary:
            print(f"Error: {project_summary['Error']}")
            return
        for tower in project_summary["Towers"]:
            for tower_name, details in tower.items():
                print(f"\n{tower_name}:")
                print("-" * 35)
                for key, value in details.items():
                    if key == "Locker Configurations":
                        print(f"{key}:")
                        for config in value:
                            print(f"  Width: {config['Width (in)']} inches")
                            print(f"  Number of Lockers: {config['Number of Lockers']}")
                            print(f"  Heights: {config['Heights (in)']}")
                    elif key == "Bill of Materials":
                        print(f"{key}:")
                        bom = value
                        print(f"  Material: {bom['material']}")
                        print(f"  Tower (0.75\"): {bom['tower_sqft']} sqft")
                        print(f"  Doors (1\"): {bom['door_sqft']} sqft")
                    elif key == "Cost Breakdown":
                        continue  # Skip old cost breakdown
                    else:
                        print(f"{key}: {value}")
        print("\nProject Totals:")
        print("-" * 35)
        for key, value in project_summary["Project Totals"].items():
            if key == "Bill of Materials":
                print(f"{key}:")
                for material, thicknesses in value.items():
                    for thickness, sqft in thicknesses.items():
                        if sqft > 0:
                            print(f"  {material}, {thickness}\": {round(sqft, 2)} sqft")
            elif key == "Financial Summary":
                print(f"{key}:")
                for sub_key, sub_value in value.items():
                    print(f"  {sub_key}: {sub_value}")
            else:
                print(f"{key}: {value}")
        print("=" * 50)


def main():
    configurator = LockerTowerConfigurator()
    lock_input_map = {
        "B": "Basic", "M": "Medium", "P": "Premier",
        "Basic": "Basic", "Medium": "Medium", "Premier": "Premier"
    }
    material_input_map = {
        "M": "MDF", "P": "Polywood", "G": "Polygood",
        "MDF": "MDF", "Polywood": "Polywood", "Polygood": "Polygood"
    }
    hinge_input_map = {
        "S": "Standard", "R": "Reinforced",
        "Standard": "Standard", "Reinforced": "Reinforced"
    }
    controller_input_map = {
        "T": "Top", "B": "Bottom", "O": "Both",
        "Top": "Top", "Bottom": "Bottom", "Both": "Both"
    }

    while True:
        print("\nLocker Tower Project Configurator\nEnter 'q' to quit")
        try:
            print("\nThird-Party Provisions")
            print("-" * 20)
            while True:
                third_party_any = input("Third party covering costs? (y/n): ").lower()
                if third_party_any in ['y', 'n']:
                    break
                print("Enter 'y' or 'n'.")
            if third_party_any == 'y':
                for item, flag in [
                    ("hinges", "third_party_hinges"), ("locks", "third_party_locks"),
                    ("material", "third_party_material"), ("labor", "third_party_labor"),
                    ("CNC cutting", "third_party_cnc")
                ]:
                    while True:
                        inp = input(f"Is {item} provided by third party? (y/n): ").lower()
                        if inp in ['y', 'n']:
                            setattr(configurator, flag, inp == 'y')
                            break
                        print("Enter 'y' or 'n'.")
            else:
                configurator.third_party_hinges = False
                configurator.third_party_locks = False
                configurator.third_party_material = False
                configurator.third_party_labor = False
                configurator.third_party_cnc = False

            num_towers_input = input("\nNumber of towers: ")
            if num_towers_input.lower() == 'q':
                print("Exiting.")
                break
            num_towers = int(num_towers_input)
            if num_towers < 1:
                raise ValueError("At least 1 tower required.")

            control_housing_tower = None
            control_input = input("Include control housing? (y/n): ").lower()
            if control_input == 'y':
                control_tower_input = input(f"Which tower (1-{num_towers})? ")
                control_housing_tower = int(control_tower_input)
                if not (1 <= control_housing_tower <= num_towers):
                    raise ValueError(f"Tower must be 1-{num_towers}.")

            tower_configs = []
            for i in range(1, num_towers + 1):
                print(f"\nConfiguring Tower {i}")
                print("-" * 20)
                height_input = input("Base tower height (36, 48, 60, 72): ")
                base_tower_height = int(height_input)
                if base_tower_height not in configurator.height_options:
                    raise ValueError(f"Height must be one of {configurator.height_options}.")

                include_control_housing = (i == control_housing_tower)

                while True:
                    controller_input = input("Lock controller location (Top/T, Bottom/B, Both/O): ").strip().capitalize()
                    if controller_input in controller_input_map:
                        lock_controller_location = controller_input_map[controller_input]
                        controller_height = configurator.lock_controller_options[lock_controller_location]
                        print(f"Lock Controller: {lock_controller_location}, adding {controller_height} inches.")
                        break
                    print("Enter Top/T, Bottom/B, or Both/O.")

                adjusted_tower_height = base_tower_height + controller_height
                effective_height = adjusted_tower_height - controller_height
                if include_control_housing:
                    effective_height -= configurator.control_housing_height

                while True:
                    material_input = input("Material (MDF/M, Polywood/P, Polygood/G): ").strip().capitalize()
                    if material_input in material_input_map:
                        material = material_input_map[material_input]
                        break
                    print("Enter MDF/M, Polywood/P, or Polygood/G.")

                while True:
                    lock_input = input("Lock type (Basic/B, Medium/M, Premier/P): ").strip().capitalize()
                    if lock_input in lock_input_map:
                        lock_type = lock_input_map[lock_input]
                        break
                    print("Enter Basic/B, Medium/M, or Premier/P.")

                while True:
                    hinge_input = input("Hinge type (Standard/S, Reinforced/R): ").strip().capitalize()
                    if hinge_input in hinge_input_map:
                        hinge_type = hinge_input_map[hinge_input]
                        break
                    print("Enter Standard/S or Reinforced/R.")

                locker_configs = []
                total_locker_height = 0
                while total_locker_height < effective_height:
                    print(f"\nRemaining height: {effective_height - total_locker_height} inches")
                    width_input = input("9-inch or 18-inch lockers? (9/18): ")
                    use_9_inch = width_input == "9"
                    num_lockers_input = input(f"Number of {'9-inch' if use_9_inch else '18-inch'} lockers (9-inch even, 2-24; 18-inch 1-24): ")
                    num_lockers = int(num_lockers_input)
                    expected_heights = num_lockers // 2 if use_9_inch else num_lockers
                    print(f"Enter {expected_heights} heights (6, 12, 18, 24, 36, 48, 60, 72) for {effective_height - total_locker_height} inches.")
                    locker_heights = []
                    for j in range(expected_heights):
                        while True:
                            height_input = input(f"Height {j+1}: ")
                            try:
                                locker_height = int(height_input)
                                if locker_height not in configurator.locker_height_options:
                                    print("Height must be 6, 12, 18, 24, 36, 48, 60, or 72.")
                                    continue
                                locker_heights.append(locker_height)
                                break
                            except ValueError:
                                print("Enter a valid number.")
                    config_height = sum(locker_heights)
                    if config_height > effective_height - total_locker_height:
                        raise ValueError(f"Heights ({config_height}\") exceed remaining ({effective_height - total_locker_height}").")
                    locker_configs.append({
                        "num_lockers": num_lockers,
                        "heights": locker_heights,
                        "use_9_inch": use_9_inch
                    })
                    total_locker_height += config_height

                if total_locker_height != effective_height:
                    print(f"Total height ({total_locker_height}\") does not match ({effective_height}\").")
                    fill_choice = input(f"Fill remaining {effective_height - total_locker_height} inches? (y/n): ").lower()
                    if fill_choice == 'y':
                        remaining_height = effective_height - total_locker_height
                        print(f"Remaining: {remaining_height} inches")
                        use_9_inch = input("Use 9-inch lockers? (y/n): ").lower() == 'y'
                        num_lockers_input = input(f"Number of {'9-inch' if use_9_inch else '18-inch'} lockers: ")
                        num_lockers = int(num_lockers_input)
                        expected_heights = num_lockers // 2 if use_9_inch else num_lockers
                        print(f"Enter {expected_heights} heights (6, 12, 18, 24, 36, 48, 60, 72) to fill {remaining_height} inches.")
                        locker_heights = []
                        height_sum = 0
                        for j in range(expected_heights):
                            while True:
                                height_input = input(f"Height {j+1}: ")
                                try:
                                    locker_height = int(height_input)
                                    if locker_height not in configurator.locker_height_options:
                                        print("Height must be 6, 12, 18, 24, 36, 48, 60, or 72.")
                                        continue
                                    locker_heights.append(locker_height)
                                    height_sum += locker_height
                                    break
                                except ValueError:
                                    print("Enter a valid number.")
                        if height_sum != remaining_height:
                            raise ValueError(f"Heights ({height_sum}\") must fill {remaining_height} inches.")
                        locker_configs.append({
                            "num_lockers": num_lockers,
                            "heights": locker_heights,
                            "use_9_inch": use_9_inch
                        })
                    else:
                        raise ValueError(f"Total height must equal {effective_height} inches.")

                tower_configs.append({
                    "locker_configs": locker_configs,
                    "base_tower_height": base_tower_height,
                    "include_control_housing": include_control_housing,
                    "material": material,
                    "lock_type": lock_type,
                    "hinge_type": hinge_type,
                    "lock_controller_location": lock_controller_location
                })

            project_summary = configurator.configure_project(tower_configs)
            configurator.display_summary(project_summary)

        except ValueError as e:
            print(f"Invalid input: {e}. Try again.")

if __name__ == "__main__":
    main()