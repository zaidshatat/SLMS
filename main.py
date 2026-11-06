import screens as sc

# Run the startup screens, then keep routing menu choices until the user exits.
def main():
    # Create the local data file if needed without changing existing contents.
    with open("students.txt", "a"):
        pass

    # Show developer details before opening the main menu.
    sc.show_developer_info()
    input("\nplease press any key to continue...")
    print(f"\nWelcome to the SLMS")

    while True:
        # Show the menu and validate the selected option.
        sc.display_main_menu()

        # Route each choice to its screen; the exit choice ends this loop.
        choice = sc.get_user_choice()

        match choice:
            case 'A':
                sc.add_student()
            case 'B':
                sc.modify_student_info()
            case 'C':
                sc.show_reports_screen()
            case 'D':
                sc.delete_student_info()
            case 'E':
                print("\nExiting the program. Goodbye!")
                break

# Start the program when this file is run directly.
if __name__ == "__main__":
    main()
