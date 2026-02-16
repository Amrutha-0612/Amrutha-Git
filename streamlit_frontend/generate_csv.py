import pandas as pd
import io

# The complete dataset string
csv_data = """ID NO.,NAME,QUANTITY,STATUS,ADDRESS,CUSTOMER NAME,COMPANY,TOT. AMT,EXPECTED DELIVERY DATE,ACTUAL DELIVERY DATE,PRIORITY,DELIVERY AGENT,NOTES,RATING BY CUSTOMER
1001,Office Ergonomic Chair - SKU 8821,5,Delivered,"123 Business Park, TechZone",Alpha Corp,12500,10-01-2025,10-01-2025,High,James Wilson,Delivered to reception,5
1002,Monitor Stand - SKU 1102,10,Pending,"45 Industrial Way, Logistics Hub",Beta Solutions,4500,12-01-2025,,Medium,Sarah Davis,Awaiting security clearance,
1003,Wireless Keyboard - Batch C,20,Delivered,"78 Corporate Ave, Finance District",Gamma Inc,8000,15-01-2025,16-01-2025,Low,Michael Brown,Delayed due to traffic,4
1004,Laptop Docking Station - Unit 5,2,In Progress,"89 Innovation Dr, Startup City",Delta Tech,3000,18-01-2025,,High,Emily White,Out for delivery,
1005,Conference Table - SKU 9982,1,Delivered,"56 Executive Blvd, Management Plaza",Epsilon Group,25000,20-01-2025,19-01-2025,High,David Miller,Early delivery requested,5
1006,Whiteboard Markers - Box 12,50,Delivered,"23 Education Ln, School District",Zeta Schools,1500,22-01-2025,22-01-2025,Low,Jennifer Garcia,Left at front desk,4.5
1007,Projector Screen - 100 inch,1,Pending,"67 Media Cir, Creative Studio",Eta Productions,5000,25-01-2025,,Medium,Robert Martinez,Address verification needed,
1008,Filing Cabinet - Metal,3,Delivered,"34 Admin St, Government Center",Theta Agency,6000,28-01-2025,30-01-2025,Medium,Linda Rodriguez,Elevator issue caused delay,3
1009,Printer Paper - A4 Case,10,Delivered,"90 Print Rd, Publishing House",Iota Press,2000,01-02-2025,01-02-2025,Low,William Hernandez,Standard delivery,5
1010,Network Switch - 24 Port,2,In Progress,"12 Server Alley, Data Center",Kappa Systems,8000,05-02-2025,,High,Elizabeth Lopez,Scheduled for afternoon,
1011,USB-C Cables - Pack 10,15,Delivered,"45 Tech Park, Software Solutions",Lambda Soft,1500,08-02-2025,08-02-2025,Low,Thomas Gonzalez,Received by IT admin,4.8
1012,Standing Desk Converter,4,Pending,"78 Wellness Way, Health Corp",Mu Health,12000,10-02-2025,,Medium,Barbara Perez,Rescheduled by client,
1013,Noise Cancelling Headphones,8,Delivered,"23 Audio Ln, Call Center",Nu Communications,16000,12-02-2025,14-02-2025,High,Joseph Sanchez,Incorrect address initially,4
1014,Webcam - HD 1080p,12,Delivered,"56 Remote Dr, Virtual Office",Xi Consultants,7200,15-02-2025,15-02-2025,Medium,Susan Clark,Handed to security,5
1015,Paper Shredder - Heavy Duty,1,In Progress,"89 Secure St, Law Firm",Omicron Legal,3500,18-02-2025,,Low,Charles Ramirez,Driver en route,
1016,Coffee Machine - Industrial,1,Delivered,"12 Breakroom Blvd, Corporate HQ",Pi Enterprises,45000,20-02-2025,20-02-2025,High,Margaret Lewis,Installation included,5
1017,Water Dispenser - Cooler,2,Delivered,"34 Hydration Ave, Gym Chain",Rho Fitness,5000,22-02-2025,25-02-2025,Medium,Christopher Allen,Vehicle breakdown delay,3.5
1018,Desk Lamp - LED,25,Pending,"90 Bright St, Design Agency",Sigma Designs,3750,25-02-2025,,Low,Jessica Young,Customer unavailable,
1019,Extension Cord - 10ft,30,Delivered,"45 Power Ln, Engineering Firm",Tau Engineering,1200,28-02-2025,28-02-2025,Low,Daniel King,Bulk delivery complete,4.9
1020,Server Rack - 42U,1,Delivered,"67 Network Dr, Cloud Services",Upsilon Cloud,15000,01-03-2025,05-03-2025,High,Nancy Scott,Customs clearance delay,4
1021,Mesh WiFi System - 3 Pack,5,In Progress,"101 Connectivity Rd, Residential Complex",SmartHomes Inc,15000,06-03-2025,,Medium,James Wilson,Package sorting,
1022,External Hard Drive - 4TB,10,Delivered,"202 Data Dr, Backup Solutions",SecureData,12000,08-03-2025,07-03-2025,High,Sarah Davis,Early delivery accepted,5
1023,Bluetooth Speaker - Portable,20,Pending,"303 Sound St, Music Store",AudioWave,5000,10-03-2025,,Low,Michael Brown,Stock pending at warehouse,
1024,Gaming Mouse - RGB,15,Delivered,"404 Gamer Ln, E-Sports Arena",ProPlay Gear,4500,12-03-2025,12-03-2025,Medium,Emily White,Received by front desk,4.7
1025,Mechanical Keyboard - Blue Switch,8,In Progress,"505 Typing Way, Coding Bootcamp",CodeAcademy,8000,15-03-2025,,High,David Miller,Out for delivery,
1026,Tablet Stand - Adjustable,12,Delivered,"606 Gadget Ave, Tech Reviewers",ReviewTech,2400,18-03-2025,20-03-2025,Low,Jennifer Garcia,Traffic delay noted,3.8
1027,Smart Watch - Fitness Tracker,6,Pending,"707 Health Blvd, Fitness Center",FitLife,9000,20-03-2025,,Medium,Robert Martinez,Customer requested hold,
1028,VR Headset - Pro,2,Delivered,"808 Virtual Pl, VR Arcade",VirtualReality Co,60000,22-03-2025,22-03-2025,High,Linda Rodriguez,Handled with care,5
1029,Drone - Camera 4K,1,Delivered,"909 Sky High Rd, Photography Studio",AerialShot,45000,25-03-2025,26-03-2025,High,William Hernandez,Signature required,4.5
1030,Action Camera - Waterproof,5,In Progress,"1010 Adventure Ln, Sports Shop",ExtremeSports,15000,28-03-2025,,Medium,Elizabeth Lopez,In transit,
1031,Portable Charger - 20000mAh,25,Delivered,"1111 Power St, Travel Agency",TravelWise,5000,30-03-2025,30-03-2025,Low,Thomas Gonzalez,Bulk order delivered,5
1032,Smart Thermostat,10,Pending,"1212 Eco Dr, Green Homes",EcoLiving,18000,02-04-2025,,Medium,Barbara Perez,Installation scheduling pending,
1033,Robot Vacuum Cleaner,3,Delivered,"1313 Clean Way, Apartment Complex",ModernLiving,21000,05-04-2025,04-04-2025,High,Joseph Sanchez,Early delivery confirmed,5
1034,Air Purifier - HEPA,4,Delivered,"1414 Fresh Air Ln, Medical Clinic",HealthFirst,16000,08-04-2025,10-04-2025,High,Susan Clark,Delay due to rain,4.2
1035,Electric Kettle - 1.7L,8,In Progress,"1515 Kitchen Rd, Cafe Chain",BrewMaster,3200,10-04-2025,,Low,Charles Ramirez,Sorting facility,
1036,Blender - High Speed,2,Delivered,"1616 Smoothie St, Juice Bar",FreshJuice,6000,12-04-2025,12-04-2025,Medium,Margaret Lewis,Delivered to manager,4.8
1037,Toaster - 4 Slice,5,Pending,"1717 Breakfast Blvd, Hotel Chain",StayComfort,2500,15-04-2025,,Low,Christopher Allen,Address update required,
1038,Microwave Oven - 20L,1,Delivered,"1818 Heat Way, Office Pantry",CorporateHub,5000,18-04-2025,18-04-2025,Medium,Jessica Young,Secure delivery,5
1039,Rice Cooker - 10 Cup,3,Delivered,"1919 Grain Ln, Restaurant",AsianBites,4500,20-04-2025,22-04-2025,Medium,Daniel King,Late due to vehicle issue,3.5
1040,Food Processor - Multi-function,2,In Progress,"2020 Chef Cir, Culinary School",ChefAcademy,8000,22-04-2025,,High,Nancy Scott,Out for delivery,
1041,Induction Cooktop,4,Delivered,"2121 Magnet Dr, Modern Kitchens",KitchenTech,10000,25-04-2025,25-04-2025,High,James Wilson,On time delivery,5
1042,Hand Mixer - 5 Speed,10,Pending,"2222 Bake St, Bakery",SweetTreats,3000,28-04-2025,,Low,Sarah Davis,Recipient unavailable,
1043,Digital Scale - Kitchen,15,Delivered,"2323 Weight Way, Nutrition Center",HealthyLife,2250,30-04-2025,01-05-2025,Low,Michael Brown,Slight delay,4.5
1044,Measuring Cups - Set,20,In Progress,"2424 Measure Ln, Cooking Class",CookEasy,1000,02-05-2025,,Low,Emily White,In transit,
1045,Chef Knife - 8 Inch,5,Delivered,"2525 Cutlery Blvd, Steakhouse",PrimeSteak,7500,05-05-2025,05-05-2025,Medium,David Miller,Handed to chef,5
1046,Cutting Board - Bamboo,10,Delivered,"2626 Prep St, Home Goods Store",HomeEssentials,2000,08-05-2025,09-05-2025,Low,Jennifer Garcia,Delivered a day late,4
1047,Non-Stick Frying Pan,8,Pending,"2727 Fry Way, Diner",AmericanDiner,4000,10-05-2025,,Medium,Robert Martinez,Awaiting payment confirmation,
1048,Saucepan - 2L,6,Delivered,"2828 Boil Ln, Soup Kitchen",CommunitySoup,3000,12-05-2025,12-05-2025,Medium,Linda Rodriguez,Delivered to volunteer,5
1049,Stock Pot - 10L,2,Delivered,"2929 Stew Dr, Catering Service",EventCatering,5000,15-05-2025,18-05-2025,High,William Hernandez,Significant delay noted,3
1050,Baking Sheet - Non-Stick,12,In Progress,"3030 Oven Rd, Pastry Shop",PastryDelight,2400,18-05-2025,,Low,Elizabeth Lopez,Package scanning,
1051,Muffin Tin - 12 Cup,10,Delivered,"3131 Cupcake Cir, Cupcake Store",CupcakeHeaven,1500,20-05-2025,20-05-2025,Low,Thomas Gonzalez,Standard service,4.8
1052,Rolling Pin - Wood,5,Pending,"3232 Dough Way, Pizzeria",PizzaExpress,500,22-05-2025,,Low,Barbara Perez,Address incomplete,
1053,Pizza Cutter - Wheel,20,Delivered,"3333 Slice St, Pizza Chain",SliceOfLife,1000,25-05-2025,25-05-2025,Low,Joseph Sanchez,Bulk order received,5
1054,Can Opener - Electric,4,Delivered,"3434 Open Dr, Senior Center",GoldenYears,1200,28-05-2025,29-05-2025,Medium,Susan Clark,One day delay,4
1055,Garlic Press - Stainless Steel,15,In Progress,"3535 Flavor Ln, Italian Restaurant",PastaPlace,2250,30-05-2025,,Low,Charles Ramirez,Driver assigned,
1056,Peeler - Y Shape,25,Delivered,"3636 Peel Blvd, Salad Bar",FreshGreens,1250,02-06-2025,02-06-2025,Low,Margaret Lewis,Left at back door,4.5
1057,Whisk - Silicone,10,Pending,"3737 Mix Way, Culinary Institute",LearnToCook,800,05-06-2025,,Low,Christopher Allen,Recipient request reschedule,
1058,Spatula - Heat Resistant,20,Delivered,"3838 Flip St, Burger Joint",BurgerKing,1600,08-06-2025,08-06-2025,Medium,Jessica Young,Delivered on time,5
1059,Tongs - Locking,15,Delivered,"3939 Grip Dr, BBQ Restaurant",SmokeHouse,1500,10-06-2025,12-06-2025,Medium,Daniel King,Delay due to weather,3.8
1060,Thermometer - Instant Read,5,Delivered,"4040 Temp Ln, Candy Shop",SweetTooth,1000,12-06-2025,12-06-2025,High,Nancy Scott,Critical for production,5"""

# Read the CSV data
try:
    df = pd.read_csv(io.StringIO(csv_data))
    
    # Save to Excel file
    output_filename = "Professional_Delivery_Data.xlsx"
    df.to_excel(output_filename, index=False)
    
    print(f"Successfully created '{output_filename}' with {len(df)} rows.")
    print("You can now open this file in Excel.")
    
except Exception as e:
    print(f"Error creating Excel file: {e}")
