import os
import pandas as pd
import numpy as np

os.makedirs('sample_data', exist_ok=True)

# -------------------------------------------------------------------------
# Practice Set 1: IT Department - Semester VI (End-Term Examination 2024-25)
# 40 Students, 5 Subjects:
# - Cloud Computing (Easy/High Avg)
# - Machine Learning (Challenging/Low Avg)
# - Cyber Security (Moderate)
# - Web Technologies (Easy/High Pass)
# - Software Engineering (Moderate)
# -------------------------------------------------------------------------
np.random.seed(101)
it_students = [
    'Aditi Sharma', 'Akash Varma', 'Ananya Deshmukh', 'Arnav Singhal', 'Avani Sen',
    'Ayush Kulkarni', 'Bhavya Hegde', 'Chetan Rao', 'Devika Pillai', 'Gautam Nambiar',
    'Harini Iyer', 'Ishaan Kapoor', 'Jaya Sundaram', 'Karan Mittal', 'Lavanya Bhatt',
    'Manasvi Ghosh', 'Mohit Choudhury', 'Naina Saxena', 'Naveen Banerjee', 'Nikita Mukhopadhyay',
    'Omkar Joshi', 'Parth Rastogi', 'Payal Agarwal', 'Prateek Mishra', 'Priya Tiwari',
    'Raghav Chauhan', 'Rashi Pandey', 'Rishi Aggarwal', 'Riya Verma', 'Rohit Bose',
    'Siddharth Nair', 'Sneha Gupta', 'Sourabh Sen', 'Srushti Patel', 'Suraj Reddy',
    'Tanmay Menin', 'Trisha Kumar', 'Varun Menon', 'Vidhi Sharma', 'Yashwant Rao'
]

it_data = []
for i, name in enumerate(it_students, start=1):
    roll = f"IT24-{i:03d}"
    if i in [1, 2, 11]:  # Top Tier
        cc = np.random.randint(92, 99)
        ml = np.random.randint(84, 94)
        cs = np.random.randint(86, 96)
        wt = np.random.randint(90, 100)
        se = np.random.randint(88, 97)
    elif i in [5, 18, 30]:  # Students with specific backlogs in Machine Learning
        cc = np.random.randint(52, 65)
        ml = np.random.randint(28, 38) # Failed
        cs = np.random.randint(45, 58)
        wt = np.random.randint(60, 72)
        se = np.random.randint(50, 62)
    elif i in [24]: # Failed in two subjects
        cc = np.random.randint(40, 48)
        ml = np.random.randint(22, 35) # Failed
        cs = np.random.randint(31, 39) # Failed
        wt = np.random.randint(55, 65)
        se = np.random.randint(42, 50)
    else:  # General healthy distribution
        cc = np.random.randint(70, 92)
        ml = np.random.randint(42, 78)
        cs = np.random.randint(55, 85)
        wt = np.random.randint(68, 94)
        se = np.random.randint(60, 86)
        
    it_data.append({
        'roll_number': roll,
        'student_name': name,
        'cloud_computing': cc,
        'machine_learning': ml,
        'cyber_security': cs,
        'web_technologies': wt,
        'software_engineering': se
    })

df_it = pd.DataFrame(it_data)
df_it.to_csv('sample_data/it_sem6_end_term_practice.csv', index=False)
df_it.to_excel('sample_data/it_sem6_end_term_practice.xlsx', index=False)


# -------------------------------------------------------------------------
# Practice Set 2: Electronics & Comm. Engg (ECE) - Sem IV (Mid-Term Assessment)
# 30 Students, 5 Subjects:
# - Signals & Systems (Tough/Low Pass Rate)
# - Analog Circuits (Moderate)
# - Digital Electronics (Easy/High Avg)
# - Electromagnetic Fields (Moderate/Tough)
# - Microprocessors (Moderate)
# Includes intentional tied toppers!
# -------------------------------------------------------------------------
np.random.seed(202)
ece_students = [
    'Aarohi Kulkarni', 'Abhinav Sen', 'Alok Gupta', 'Amrita Nair', 'Anand Verma',
    'Anika Patel', 'Archit Deshmukh', 'Ashwin Rao', 'Deepika Pillai', 'Divya Sundaram',
    'Girish Bhatt', 'Hema Nambiar', 'Jatin Choudhury', 'Komal Saxena', 'Madhav Banerjee',
    'Neha Mittal', 'Nitin Ghosh', 'Pallavi Agarwal', 'Pankaj Tiwari', 'Pooja Hegde',
    'Pranav Rastogi', 'Preeti Mishra', 'Rajesh Chauhan', 'Ritu Pandey', 'Sachin Aggarwal',
    'Sameer Bose', 'Sanjay Kapoor', 'Sarita Mukhopadhyay', 'Shikha Joshi', 'Vikas Reddy'
]

ece_data = []
for i, name in enumerate(ece_students, start=1):
    roll = f"ECE24-{i:03d}"
    # Intentional tied toppers at ranks 1 and 2
    if i == 1:
        ss, ac, de, emf, mp = 94, 91, 98, 89, 93  # Total 465
    elif i == 2:
        ss, ac, de, emf, mp = 91, 94, 97, 90, 93  # Total 465 (Exact Tie!)
    elif i in [8, 14, 22]: # Difficult subjects struggle
        ss = np.random.randint(24, 37)  # Failed in Signals
        ac = np.random.randint(45, 60)
        de = np.random.randint(65, 78)
        emf = np.random.randint(30, 39) # Failed in EMF
        mp = np.random.randint(45, 58)
    else:
        ss = np.random.randint(42, 80)
        ac = np.random.randint(52, 84)
        de = np.random.randint(72, 95)
        emf = np.random.randint(45, 82)
        mp = np.random.randint(58, 88)

    ece_data.append({
        'roll_number': roll,
        'student_name': name,
        'signals_and_systems': ss,
        'analog_circuits': ac,
        'digital_electronics': de,
        'electromagnetic_fields': emf,
        'microprocessors': mp
    })

df_ece = pd.DataFrame(ece_data)
df_ece.to_csv('sample_data/ece_sem4_midterm_practice.csv', index=False)
df_ece.to_excel('sample_data/ece_sem4_midterm_practice.xlsx', index=False)


# -------------------------------------------------------------------------
# Practice Set 3: Mechanical Engineering (ME) - Sem V (Annual Term 2023-24)
# 35 Students, 5 Subjects:
# - Thermodynamics (Moderate)
# - Fluid Mechanics (Challenging)
# - Heat Transfer (Moderate)
# - Machine Design (Challenging)
# - Manufacturing Processes (Easy)
# -------------------------------------------------------------------------
np.random.seed(303)
me_students = [
    'Aakash Pillai', 'Aditya Sen', 'Ajay Varma', 'Amit Deshmukh', 'Aniket Singhal',
    'Anil Kulkarni', 'Anupam Rao', 'Bharat Nair', 'Bipin Gupta', 'Chandan Patel',
    'Deepak Sundaram', 'Dhanush Bhatt', 'Dilip Nambiar', 'Ganesh Choudhury', 'Hari Saxena',
    'Jayesh Banerjee', 'Kailash Ghosh', 'Kartik Mittal', 'Lokesh Agarwal', 'Mahesh Tiwari',
    'Mukesh Hegde', 'Nagesh Rastogi', 'Naveen Mishra', 'Pawan Chauhan', 'Prakash Pandey',
    'Ramesh Aggarwal', 'Ravi Bose', 'Santosh Mukhopadhyay', 'Shankar Joshi', 'Subhash Reddy',
    'Suresh Kapoor', 'Tarun Kumar', 'Umesh Menon', 'Vijay Sharma', 'Vinod Rao'
]

me_data = []
for i, name in enumerate(me_students, start=1):
    roll = f"ME23-{i:03d}"
    if i in [1, 7]: # Top Performers
        td = np.random.randint(88, 96)
        fm = np.random.randint(85, 94)
        ht = np.random.randint(90, 98)
        md = np.random.randint(86, 95)
        mp = np.random.randint(92, 100)
    elif i in [12, 20, 27]: # Multiple backlogs
        td = np.random.randint(32, 42)
        fm = np.random.randint(22, 36) # Failed
        ht = np.random.randint(40, 52)
        md = np.random.randint(28, 38) # Failed
        mp = np.random.randint(55, 68)
    else:
        td = np.random.randint(52, 85)
        fm = np.random.randint(40, 78)
        ht = np.random.randint(56, 88)
        md = np.random.randint(45, 80)
        mp = np.random.randint(65, 94)

    me_data.append({
        'roll_number': roll,
        'student_name': name,
        'thermodynamics': td,
        'fluid_mechanics': fm,
        'heat_transfer': ht,
        'machine_design': md,
        'manufacturing_processes': mp
    })

df_me = pd.DataFrame(me_data)
df_me.to_csv('sample_data/me_sem5_annual_practice.csv', index=False)
df_me.to_excel('sample_data/me_sem5_annual_practice.xlsx', index=False)

print("Created 3 comprehensive practice datasets (both .csv and .xlsx) in sample_data/")
