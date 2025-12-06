# imports
import pandas as pd
from matplotlib import pyplot as plt

# import csv
data = pd.read_csv(r'C:\Users\Gursharan JIT SINGH\Desktop\DeliveryTracker_Python_EL.csv')


def lateDelivery():

    data["EXPECTED DELIVERY DATE"] = pd.to_datetime(data["EXPECTED DELIVERY DATE"], dayfirst=True, errors='coerce')
    data["ACTUAL DELIVERY DATE"] = pd.to_datetime(data["ACTUAL DELIVERY DATE"], dayfirst=True, errors='coerce')
    data["Duration"] = data["ACTUAL DELIVERY DATE"] - data["EXPECTED DELIVERY DATE"]

    delayed_df = data[data["Duration"] > pd.Timedelta(days=0)]
    delivered_df = data.dropna(subset=["ACTUAL DELIVERY DATE"]).copy()

    print(delayed_df)
    plotDeliveryData(delivered_df)


def plotDeliveryData(delivered_df):
    print('-' * 40)
    print('Delivery Performance'.center(40, ' '))
    print('-' * 40)

    # Categorize deliveries
    delivered_df["Delivery Status"] = delivered_df["Duration"].apply(lambda x: "Late" if x > pd.Timedelta(days=0) else "On Time")
    #data["Delivery Status"] = data["Days Late"].apply(checkLateDelivery())

    # Count them
    status_counts = delivered_df["Delivery Status"].value_counts()

    # Plot
    colors = ['green' if status == 'On Time' else 'red' for status in status_counts.index]
    status_counts.plot(kind='bar', color=colors, figsize=(6,4))

    plt.title('Delivery Performance: On-Time vs Late')
    plt.xlabel('Delivery Status')
    plt.ylabel('Number of Deliveries')
    plt.xticks(rotation=0)

    # Add value labels on top of bars
    for index, value in enumerate(status_counts):
        plt.text(index, value + 0.2, str(value), ha='center', va='bottom', fontsize=10)

    plt.tight_layout()
    plt.show()
    mainmenu()

def showdata():
    print('-' * 40)
    print('Display Data'.center(40, ' '))
    print('-' * 40)
    print(data)
    input('Enter to continue')
    mainmenu()


def analysis():
    print('-'*40)
    print('Data Analysis'.center(40, ' '))
    print('-'*40)
    
    # 1. Workload by Responsible Person
    if 'DELIVERY AGENT' in data.columns:
        print("\n Items Assigned Per Person:")
        person_workload = data['DELIVERY AGENT'].value_counts()
        print(person_workload)

    # 2. Work Distribution by Priority
    if 'PRIORITY' in data.columns:
        print("\n Workload Distribution by Priority:")
        priority_counts = data['PRIORITY'].value_counts()
        print(priority_counts)
    else:
        print("\n Priority data not available (missing 'PRIORITY' column).")

    # 3. Special Instructions/Notes Analysis
    if 'NOTES' in data.columns:
        data['NOTES_CLEAN'] = data['NOTES'].fillna('').astype(str).str.strip()
        items_with_notes = data[data['NOTES_CLEAN'] != '']
        
        print("\n Special Instructions/Issues:")
        print(f"   Total items with notes/special instructions: {len(items_with_notes)}")
        
        if not items_with_notes.empty:
            print("   List of Items with Notes:")
            print(items_with_notes[['ID NO.', 'NAME', 'STATUS', 'NOTES']].to_string(index=False))
    
        # Clean up the temporary column before continuing
        if 'NOTES_CLEAN' in data.columns:
            data.drop(columns=['NOTES_CLEAN'], inplace=True, errors='ignore')

    input('\nEnter to continue')
    mainmenu()


def graphplot():
    print('-' * 40)
    print('Data Visualization'.center(40, ' '))
    print('-' * 40)
    print('1. Progress Status')
    print('2. Workload by Person')
    print('3. Workload by Priority Level')
    print('4. Exit')
    gch = int(input("Enter graph choice: "))
    if gch ==1:
        
        status_counts = data['STATUS'].value_counts()
        status_counts.plot(kind='bar')
        plt.title('Progress Status')
        plt.xlabel('Status')
        plt.ylabel('Number of Products')
        plt.xticks(rotation=45)
        for index, value in enumerate(status_counts):
            plt.text(index, value + 0.1, str(value), ha='center', va='bottom')
        plt.tight_layout()
        plt.show()
        input('Enter to continue')
        graphplot()


   

    # --- Graph 2 (axes[1]): Workload by Responsible Person ---
    elif gch==2:
        
        person_workload = data['DELIVERY AGENT'].value_counts()
        person_workload.plot(kind='bar', color='lightcoral')
        plt.title('Workload by Person')
        plt.xlabel('Responsible Person/Team')
        plt.ylabel('Number of Items')
        plt.xticks(rotation=45)
        for index, value in enumerate(person_workload):
            plt.text(index, value + 0.1, str(value), ha='center', va='bottom')
        plt.tight_layout()
        plt.show()
        input('Enter to continue')
        graphplot()
    
    # --- Graph 3 (axes[2]): Workload by Priority ---
    elif gch==3:
        priority_counts = data['PRIORITY'].value_counts()
        priority_counts.plot(kind='bar', color='darkorange')
        plt.title('Workload by Priority Level')
        plt.xlabel('Priority Level')
        plt.ylabel('Number of Items')
        plt.xticks(rotation=45)
        for index, value in enumerate(priority_counts):
            plt.text(index, value + 0.1, str(value), ha='center', va='bottom')
        plt.tight_layout()
        plt.show()
        input('Enter to continue')
        graphplot()
    
    elif gch==4:
        mainmenu()
        
    

def mainmenu():
    print('-' * 40)
    print('Delivery Progress'.center(40, ' '))
    print('-' * 40)
    print('1. Display Data')
    print('2. Data Analysis')
    print('3. Data Graph Plotting')
    print('4. Tracking Late Delivery')
    print('5. Exit')
    choiceInput = int(input('Enter choice number: '))
    if choiceInput == 1:
        showdata()
        print('\n')
    elif choiceInput == 2:
        analysis()
        print('\n')
    elif choiceInput == 3:
        graphplot()
        print('\n')
    elif(choiceInput == 4):
        lateDelivery()
    elif choiceInput == 5:
        print('Thank You!!!')
    else:
        print("Invalid input! Please enter correct input")
        mainmenu()


mainmenu()

