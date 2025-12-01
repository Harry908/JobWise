"""Analyze the structure of the Epic job posting."""

EPIC_JOB = """Software Engineer
Epic
Bellevue, WA

About the job
Please note that this position is based on our campus in Madison, WI, and requires relocation to the area. We recruit nationally and provide financial relocation assistance.

Code that saves lives. 

As a software developer at Epic, you'll write software that impacts the lives of 325 million patients around the world. Working in your own office, surrounded by thousands of high-caliber developers, you'll use modern development methodologies and employ user-centered design, analytics, and machine learning tools to drive innovation in healthcare. Using leading-edge technologies and languages like JS, TS, and C#, you'll invent better ways to reduce medical errors, streamline record sharing between hospitals, and provide the quality of care a patient deserves. Learn more about our team at https://careers.epic.com/jobs/softwaredevelopment/.

Write software for the most innovative health systems on the planet.

The top-ranked health systems in U.S. News and World Report are Epic customers. Our community includes major systems like the Mayo Clinic, Johns Hopkins, Cleveland Clinic, and Kaiser Permanente, as well as leading academic medical centers at the University of Wisconsin, University of Michigan, University of California, University of Texas, The Ohio State University, and many more.

Live affordably in a city known for its rising tech talent.

Epic is located just outside Madison, Wisconsin, the second fastest growing market for tech talent in the United States and home to the state capital and the University of Wisconsin. Madison, a city surrounded by water, has received accolades for being the greenest city in America (NerdWallet), the best city for renters (SmartAsset), the fittest city in America (Fitbit), and the third best metro in the US for young professionals (Forbes Advisor).

More than just important work.

Our uniquely themed campus was designed to heighten your ability to get stuff done in your office, a conference room, or by the fireplace in a comfy chair. All meals are restaurant-quality but cost only a few dollars, and they're prepared by a team comprised of kitchen talent from restaurants around the country. And, after five years here, you'll earn a four-week sabbatical anywhere in the world. Staff have kayaked in Patagonia, attended a Beyoncé concert in Ireland, built a library in Tanzania, and run a marathon in Antarctica.

We offer comprehensive benefits to keep you healthy and happy as you grow in your life and career, and your merit-based compensation will reflect the impact your work has on the company and our customers. You'll also be eligible for annual raises and bonuses, as well as stock grants, which give you an even greater stake in the success of Epic and our customers. Healthcare is global, and building the best ideas from around the world into Epic software is a point of pride. As an Equal Opportunity Employer, we know that inclusive teams design software that supports the delivery of quality care for all patients, so diversity, equity, and inclusion are written into our principles. Please see our full non-discrimination statement at https://careers.epic.com/EEO.

Relocation to the Madison, WI area (Reimbursed)
BS/BA or greater in Computer Science, Mathematics, Software Engineering, Computer Engineering, or a related field
A history of academic excellence or professional success
Eligible to work in the United States without visa sponsorship (persons with appropriate qualifications and eligible for TN status under NAFTA may apply)
COVID-19 vaccination"""

# Print with line numbers
lines = EPIC_JOB.split('\n')
print("Structure analysis:")
print("=" * 100)

for i, line in enumerate(lines):
    if line.strip():
        print(f"Line {i:3d}: {line[:100]}")

print("\n" + "=" * 100)
print("\nKey observations:")
print("- Lines 0-2: Title, Company, Location")
print("- Lines 4-24: Main description and benefits narrative")
print("- Lines 26-30: Actual requirements (NO HEADING!)")
print("\nThe requirements section starts after the EEO statement")
print("They appear as plain lines without bullets or a header")
