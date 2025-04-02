import json
import re
from typing import List, Dict, Any

# --- Comprehensive Member Info (Derived from WDOD_test HTML) ---
# Source of truth for party info and adding missing members.

rep_info = {
    "Jerry Carl": {"name": "Jerry Carl", "state": "Alabama", "district": "1", "party": "Republican", "website": "https://carl.house.gov"},
    "Barry Moore": {"name": "Barry Moore", "state": "Alabama", "district": "2", "party": "Republican", "website": "https://barrymoore.house.gov"},
    "Mike Rogers": {"name": "Mike Rogers", "state": "Alabama", "district": "3", "party": "Republican", "website": "https://mikerogers.house.gov"},
    "Robert Aderholt": {"name": "Robert Aderholt", "state": "Alabama", "district": "4", "party": "Republican", "website": "https://aderholt.house.gov"},
    "Dale Strong": {"name": "Dale Strong", "state": "Alabama", "district": "5", "party": "Republican", "website": "https://strong.house.gov"},
    "Gary Palmer": {"name": "Gary Palmer", "state": "Alabama", "district": "6", "party": "Republican", "website": "https://palmer.house.gov"},
    "Terri Sewell": {"name": "Terri Sewell", "state": "Alabama", "district": "7", "party": "Democrat", "website": "https://sewell.house.gov"},
    "Mary Peltola": {"name": "Mary Peltola", "state": "Alaska", "district": "At-Large", "party": "Democrat", "website": "https://peltola.house.gov"},
    "David Schweikert": {"name": "David Schweikert", "state": "Arizona", "district": "1", "party": "Republican", "website": "https://schweikert.house.gov"},
    "Eli Crane": {"name": "Eli Crane", "state": "Arizona", "district": "2", "party": "Republican", "website": "https://crane.house.gov"},
    "Ruben Gallego": {"name": "Ruben Gallego", "state": "Arizona", "district": "3", "party": "Democrat", "website": "https://rubengallego.house.gov"},
    "Greg Stanton": {"name": "Greg Stanton", "state": "Arizona", "district": "4", "party": "Democrat", "website": "https://stanton.house.gov"},
    "Andy Biggs": {"name": "Andy Biggs", "state": "Arizona", "district": "5", "party": "Republican", "website": "https://biggs.house.gov"},
    "Juan Ciscomani": {"name": "Juan Ciscomani", "state": "Arizona", "district": "6", "party": "Republican", "website": "https://ciscomani.house.gov"},
    "Raúl Grijalva": {"name": "Raúl Grijalva", "state": "Arizona", "district": "7", "party": "Democrat", "website": "https://grijalva.house.gov"},
    "Debbie Lesko": {"name": "Debbie Lesko", "state": "Arizona", "district": "8", "party": "Republican", "website": "https://lesko.house.gov"},
    "Paul Gosar": {"name": "Paul Gosar", "state": "Arizona", "district": "9", "party": "Republican", "website": "https://gosar.house.gov"},
    "Rick Crawford": {"name": "Rick Crawford", "state": "Arkansas", "district": "1", "party": "Republican", "website": "https://crawford.house.gov"},
    "French Hill": {"name": "French Hill", "state": "Arkansas", "district": "2", "party": "Republican", "website": "https://hill.house.gov"},
    "Steve Womack": {"name": "Steve Womack", "state": "Arkansas", "district": "3", "party": "Republican", "website": "https://womack.house.gov"},
    "Bruce Westerman": {"name": "Bruce Westerman", "state": "Arkansas", "district": "4", "party": "Republican", "website": "https://westerman.house.gov"},
    "Doug LaMalfa": {"name": "Doug LaMalfa", "state": "California", "district": "1", "party": "Republican", "website": "https://lamalfa.house.gov"},
    "Jared Huffman": {"name": "Jared Huffman", "state": "California", "district": "2", "party": "Democrat", "website": "https://huffman.house.gov"},
    "Kevin Kiley": {"name": "Kevin Kiley", "state": "California", "district": "3", "party": "Republican", "website": "https://kiley.house.gov"},
    "Mike Thompson": {"name": "Mike Thompson", "state": "California", "district": "4", "party": "Democrat", "website": "https://mikethompson.house.gov"},
    "Tom McClintock": {"name": "Tom McClintock", "state": "California", "district": "5", "party": "Republican", "website": "https://mcclintock.house.gov"},
    "Ami Bera": {"name": "Ami Bera", "state": "California", "district": "6", "party": "Democrat", "website": "https://bera.house.gov"},
    "Doris Matsui": {"name": "Doris Matsui", "state": "California", "district": "7", "party": "Democrat", "website": "https://matsui.house.gov"},
    "John Garamendi": {"name": "John Garamendi", "state": "California", "district": "8", "party": "Democrat", "website": "https://garamendi.house.gov"},
    "Josh Harder": {"name": "Josh Harder", "state": "California", "district": "9", "party": "Democrat", "website": "https://harder.house.gov"},
    "Mark DeSaulnier": {"name": "Mark DeSaulnier", "state": "California", "district": "10", "party": "Democrat", "website": "https://desaulnier.house.gov"},
    "Nancy Pelosi": {"name": "Nancy Pelosi", "state": "California", "district": "11", "party": "Democrat", "website": "https://pelosi.house.gov"},
    "Barbara Lee": {"name": "Barbara Lee", "state": "California", "district": "12", "party": "Democrat", "website": "https://lee.house.gov"},
    "John Duarte": {"name": "John Duarte", "state": "California", "district": "13", "party": "Republican", "website": "https://duarte.house.gov"},
    "Eric Swalwell": {"name": "Eric Swalwell", "state": "California", "district": "14", "party": "Democrat", "website": "https://swalwell.house.gov"},
    "Kevin Mullin": {"name": "Kevin Mullin", "state": "California", "district": "15", "party": "Democrat", "website": "https://mullin.house.gov"},
    "Anna Eshoo": {"name": "Anna Eshoo", "state": "California", "district": "16", "party": "Democrat", "website": "https://eshoo.house.gov"},
    "Ro Khanna": {"name": "Ro Khanna", "state": "California", "district": "17", "party": "Democrat", "website": "https://khanna.house.gov"},
    "Zoe Lofgren": {"name": "Zoe Lofgren", "state": "California", "district": "18", "party": "Democrat", "website": "https://lofgren.house.gov"},
    "Jimmy Panetta": {"name": "Jimmy Panetta", "state": "California", "district": "19", "party": "Democrat", "website": "https://panetta.house.gov"},
    "Kevin McCarthy": {"name": "Kevin McCarthy", "state": "California", "district": "20", "party": "Republican", "website": "https://kevinmccarthy.house.gov"},
    "Jim Costa": {"name": "Jim Costa", "state": "California", "district": "21", "party": "Democrat", "website": "https://costa.house.gov"},
    "David Valadao": {"name": "David Valadao", "state": "California", "district": "22", "party": "Republican", "website": "https://valadao.house.gov"},
    "Jay Obernolte": {"name": "Jay Obernolte", "state": "California", "district": "23", "party": "Republican", "website": "https://obernolte.house.gov"},
    "Salud Carbajal": {"name": "Salud Carbajal", "state": "California", "district": "24", "party": "Democrat", "website": "https://carbajal.house.gov"},
    "Raul Ruiz": {"name": "Raul Ruiz", "state": "California", "district": "25", "party": "Democrat", "website": "https://ruiz.house.gov"},
    "Julia Brownley": {"name": "Julia Brownley", "state": "California", "district": "26", "party": "Democrat", "website": "https://brownley.house.gov"},
    "Mike Garcia": {"name": "Mike Garcia", "state": "California", "district": "27", "party": "Republican", "website": "https://mikegarcia.house.gov"},
    "Judy Chu": {"name": "Judy Chu", "state": "California", "district": "28", "party": "Democrat", "website": "https://chu.house.gov"},
    "Tony Cárdenas": {"name": "Tony Cárdenas", "state": "California", "district": "29", "party": "Democrat", "website": "https://cardenas.house.gov"},
    "Adam Schiff": {"name": "Adam Schiff", "state": "California", "district": "30", "party": "Democrat", "website": "https://schiff.house.gov"},
    "Grace Napolitano": {"name": "Grace Napolitano", "state": "California", "district": "31", "party": "Democrat", "website": "https://napolitano.house.gov"},
    "Brad Sherman": {"name": "Brad Sherman", "state": "California", "district": "32", "party": "Democrat", "website": "https://sherman.house.gov"},
    "Pete Aguilar": {"name": "Pete Aguilar", "state": "California", "district": "33", "party": "Democrat", "website": "https://aguilar.house.gov"},
    "Jimmy Gomez": {"name": "Jimmy Gomez", "state": "California", "district": "34", "party": "Democrat", "website": "https://gomez.house.gov"},
    "Norma Torres": {"name": "Norma Torres", "state": "California", "district": "35", "party": "Democrat", "website": "https://torres.house.gov"},
    "Ted Lieu": {"name": "Ted Lieu", "state": "California", "district": "36", "party": "Democrat", "website": "https://lieu.house.gov"},
    "Sydney Kamlager-Dove": {"name": "Sydney Kamlager-Dove", "state": "California", "district": "37", "party": "Democrat", "website": "https://kamlager-dove.house.gov"},
    "Linda Sánchez": {"name": "Linda Sánchez", "state": "California", "district": "38", "party": "Democrat", "website": "https://lindasanchez.house.gov"},
    "Mark Takano": {"name": "Mark Takano", "state": "California", "district": "39", "party": "Democrat", "website": "https://takano.house.gov"},
    "Young Kim": {"name": "Young Kim", "state": "California", "district": "40", "party": "Republican", "website": "https://youngkim.house.gov"},
    "Ken Calvert": {"name": "Ken Calvert", "state": "California", "district": "41", "party": "Republican", "website": "https://calvert.house.gov"},
    "Robert Garcia": {"name": "Robert Garcia", "state": "California", "district": "42", "party": "Democrat", "website": "https://robertgarcia.house.gov"},
    "Maxine Waters": {"name": "Maxine Waters", "state": "California", "district": "43", "party": "Democrat", "website": "https://waters.house.gov"},
    "Nanette Barragán": {"name": "Nanette Barragán", "state": "California", "district": "44", "party": "Democrat", "website": "https://barragan.house.gov"},
    "Michelle Steel": {"name": "Michelle Steel", "state": "California", "district": "45", "party": "Republican", "website": "https://steel.house.gov"},
    "Lou Correa": {"name": "Lou Correa", "state": "California", "district": "46", "party": "Democrat", "website": "https://correa.house.gov"},
    "Katie Porter": {"name": "Katie Porter", "state": "California", "district": "47", "party": "Democrat", "website": "https://porter.house.gov"},
    "Darrell Issa": {"name": "Darrell Issa", "state": "California", "district": "48", "party": "Republican", "website": "https://issa.house.gov"},
    "Mike Levin": {"name": "Mike Levin", "state": "California", "district": "49", "party": "Democrat", "website": "https://mikelevin.house.gov"},
    "Scott Peters": {"name": "Scott Peters", "state": "California", "district": "50", "party": "Democrat", "website": "https://scottpeters.house.gov"},
    "Sara Jacobs": {"name": "Sara Jacobs", "state": "California", "district": "51", "party": "Democrat", "website": "https://sarajacobs.house.gov"},
    "Juan Vargas": {"name": "Juan Vargas", "state": "California", "district": "52", "party": "Democrat", "website": "https://vargas.house.gov"},
    "Diana DeGette": {"name": "Diana DeGette", "state": "Colorado", "district": "1", "party": "Democrat", "website": "https://degette.house.gov"},
    "Joe Neguse": {"name": "Joe Neguse", "state": "Colorado", "district": "2", "party": "Democrat", "website": "https://neguse.house.gov"},
    "Lauren Boebert": {"name": "Lauren Boebert", "state": "Colorado", "district": "3", "party": "Republican", "website": "https://boebert.house.gov"},
    "Ken Buck": {"name": "Ken Buck", "state": "Colorado", "district": "4", "party": "Republican", "website": "https://buck.house.gov"},
    "Doug Lamborn": {"name": "Doug Lamborn", "state": "Colorado", "district": "5", "party": "Republican", "website": "https://lamborn.house.gov"},
    "Jason Crow": {"name": "Jason Crow", "state": "Colorado", "district": "6", "party": "Democrat", "website": "https://crow.house.gov"},
    "Brittany Pettersen": {"name": "Brittany Pettersen", "state": "Colorado", "district": "7", "party": "Democrat", "website": "https://pettersen.house.gov"},
    "Yadira Caraveo": {"name": "Yadira Caraveo", "state": "Colorado", "district": "8", "party": "Democrat", "website": "https://caraveo.house.gov"},
    "John Larson": {"name": "John Larson", "state": "Connecticut", "district": "1", "party": "Democrat", "website": "https://larson.house.gov"},
    "Joe Courtney": {"name": "Joe Courtney", "state": "Connecticut", "district": "2", "party": "Democrat", "website": "https://courtney.house.gov"},
    "Rosa DeLauro": {"name": "Rosa DeLauro", "state": "Connecticut", "district": "3", "party": "Democrat", "website": "https://delauro.house.gov"},
    "Jim Himes": {"name": "Jim Himes", "state": "Connecticut", "district": "4", "party": "Democrat", "website": "https://himes.house.gov"},
    "Jahana Hayes": {"name": "Jahana Hayes", "state": "Connecticut", "district": "5", "party": "Democrat", "website": "https://hayes.house.gov"},
    "Lisa Blunt Rochester": {"name": "Lisa Blunt Rochester", "state": "Delaware", "district": "At-Large", "party": "Democrat", "website": "https://bluntrochester.house.gov"},
    "Matt Gaetz": {"name": "Matt Gaetz", "state": "Florida", "district": "1", "party": "Republican", "website": "https://gaetz.house.gov"},
    "Neal Dunn": {"name": "Neal Dunn", "state": "Florida", "district": "2", "party": "Republican", "website": "https://dunn.house.gov"},
    "Kat Cammack": {"name": "Kat Cammack", "state": "Florida", "district": "3", "party": "Republican", "website": "https://cammack.house.gov"},
    "Aaron Bean": {"name": "Aaron Bean", "state": "Florida", "district": "4", "party": "Republican", "website": "https://bean.house.gov"},
    "John Rutherford": {"name": "John Rutherford", "state": "Florida", "district": "5", "party": "Republican", "website": "https://rutherford.house.gov"},
    "Michael Waltz": {"name": "Michael Waltz", "state": "Florida", "district": "6", "party": "Republican", "website": "https://waltz.house.gov"},
    "Cory Mills": {"name": "Cory Mills", "state": "Florida", "district": "7", "party": "Republican", "website": "https://mills.house.gov"},
    "Bill Posey": {"name": "Bill Posey", "state": "Florida", "district": "8", "party": "Republican", "website": "https://posey.house.gov"},
    "Darren Soto": {"name": "Darren Soto", "state": "Florida", "district": "9", "party": "Democrat", "website": "https://soto.house.gov"},
    "Maxwell Frost": {"name": "Maxwell Frost", "state": "Florida", "district": "10", "party": "Democrat", "website": "https://frost.house.gov"},
    "Daniel Webster": {"name": "Daniel Webster", "state": "Florida", "district": "11", "party": "Republican", "website": "https://webster.house.gov"},
    "Gus Bilirakis": {"name": "Gus Bilirakis", "state": "Florida", "district": "12", "party": "Republican", "website": "https://bilirakis.house.gov"},
    "Anna Paulina Luna": {"name": "Anna Paulina Luna", "state": "Florida", "district": "13", "party": "Republican", "website": "https://luna.house.gov"},
    "Kathy Castor": {"name": "Kathy Castor", "state": "Florida", "district": "14", "party": "Democrat", "website": "https://castor.house.gov"},
    "Laurel Lee": {"name": "Laurel Lee", "state": "Florida", "district": "15", "party": "Republican", "website": "https://lee.house.gov"},
    "Vern Buchanan": {"name": "Vern Buchanan", "state": "Florida", "district": "16", "party": "Republican", "website": "https://buchanan.house.gov"},
    "Greg Steube": {"name": "Greg Steube", "state": "Florida", "district": "17", "party": "Republican", "website": "https://steube.house.gov"},
    "Scott Franklin": {"name": "Scott Franklin", "state": "Florida", "district": "18", "party": "Republican", "website": "https://franklin.house.gov"},
    "Byron Donalds": {"name": "Byron Donalds", "state": "Florida", "district": "19", "party": "Republican", "website": "https://donalds.house.gov"},
    "Sheila Cherfilus-McCormick": {"name": "Sheila Cherfilus-McCormick", "state": "Florida", "district": "20", "party": "Democrat", "website": "https://cherfilus-mccormick.house.gov"},
    "Brian Mast": {"name": "Brian Mast", "state": "Florida", "district": "21", "party": "Republican", "website": "https://mast.house.gov"},
    "Lois Frankel": {"name": "Lois Frankel", "state": "Florida", "district": "22", "party": "Democrat", "website": "https://frankel.house.gov"},
    "Jared Moskowitz": {"name": "Jared Moskowitz", "state": "Florida", "district": "23", "party": "Democrat", "website": "https://moskowitz.house.gov"},
    "Frederica Wilson": {"name": "Frederica Wilson", "state": "Florida", "district": "24", "party": "Democrat", "website": "https://wilson.house.gov"},
    "Debbie Wasserman Schultz": {"name": "Debbie Wasserman Schultz", "state": "Florida", "district": "25", "party": "Democrat", "website": "https://wassermanschultz.house.gov"},
    "Mario Díaz-Balart": {"name": "Mario Díaz-Balart", "state": "Florida", "district": "26", "party": "Republican", "website": "https://diaz-balart.house.gov"},
    "Maria Elvira Salazar": {"name": "Maria Elvira Salazar", "state": "Florida", "district": "27", "party": "Republican", "website": "https://salazar.house.gov"},
    "Carlos Giménez": {"name": "Carlos Giménez", "state": "Florida", "district": "28", "party": "Republican", "website": "https://gimenez.house.gov"},
    "Buddy Carter": {"name": "Buddy Carter", "state": "Georgia", "district": "1", "party": "Republican", "website": "https://buddycarter.house.gov"},
    "Sanford Bishop": {"name": "Sanford Bishop", "state": "Georgia", "district": "2", "party": "Democrat", "website": "https://bishop.house.gov"},
    "Drew Ferguson": {"name": "Drew Ferguson", "state": "Georgia", "district": "3", "party": "Republican", "website": "https://ferguson.house.gov"},
    "Hank Johnson": {"name": "Hank Johnson", "state": "Georgia", "district": "4", "party": "Democrat", "website": "https://hankjohnson.house.gov"},
    "Nikema Williams": {"name": "Nikema Williams", "state": "Georgia", "district": "5", "party": "Democrat", "website": "https://nikemawilliams.house.gov"},
    "Rich McCormick": {"name": "Rich McCormick", "state": "Georgia", "district": "6", "party": "Republican", "website": "https://mccormick.house.gov"},
    "Lucy McBath": {"name": "Lucy McBath", "state": "Georgia", "district": "7", "party": "Democrat", "website": "https://mcbath.house.gov"},
    "Austin Scott": {"name": "Austin Scott", "state": "Georgia", "district": "8", "party": "Republican", "website": "https://austinscott.house.gov"},
    "Andrew Clyde": {"name": "Andrew Clyde", "state": "Georgia", "district": "9", "party": "Republican", "website": "https://clyde.house.gov"},
    "Mike Collins": {"name": "Mike Collins", "state": "Georgia", "district": "10", "party": "Republican", "website": "https://collins.house.gov"},
    "Barry Loudermilk": {"name": "Barry Loudermilk", "state": "Georgia", "district": "11", "party": "Republican", "website": "https://loudermilk.house.gov"},
    "Rick Allen": {"name": "Rick Allen", "state": "Georgia", "district": "12", "party": "Republican", "website": "https://allen.house.gov"},
    "David Scott": {"name": "David Scott", "state": "Georgia", "district": "13", "party": "Democrat", "website": "https://davidscott.house.gov"},
    "Marjorie Taylor Greene": {"name": "Marjorie Taylor Greene", "state": "Georgia", "district": "14", "party": "Republican", "website": "https://greene.house.gov"},
    "Ed Case": {"name": "Ed Case", "state": "Hawaii", "district": "1", "party": "Democrat", "website": "https://case.house.gov"},
    "Jill Tokuda": {"name": "Jill Tokuda", "state": "Hawaii", "district": "2", "party": "Democrat", "website": "https://tokuda.house.gov"},
    "Russ Fulcher": {"name": "Russ Fulcher", "state": "Idaho", "district": "1", "party": "Republican", "website": "https://fulcher.house.gov"},
    "Mike Simpson": {"name": "Mike Simpson", "state": "Idaho", "district": "2", "party": "Republican", "website": "https://simpson.house.gov"},
    "Jonathan Jackson": {"name": "Jonathan Jackson", "state": "Illinois", "district": "1", "party": "Democrat", "website": "https://jackson.house.gov"},
    "Robin Kelly": {"name": "Robin Kelly", "state": "Illinois", "district": "2", "party": "Democrat", "website": "https://robinkelly.house.gov"},
    "Delia Ramirez": {"name": "Delia Ramirez", "state": "Illinois", "district": "3", "party": "Democrat", "website": "https://ramirez.house.gov"},
    "Chuy García": {"name": "Chuy García", "state": "Illinois", "district": "4", "party": "Democrat", "website": "https://chuygarcia.house.gov"},
    "Mike Quigley": {"name": "Mike Quigley", "state": "Illinois", "district": "5", "party": "Democrat", "website": "https://quigley.house.gov"},
    "Sean Casten": {"name": "Sean Casten", "state": "Illinois", "district": "6", "party": "Democrat", "website": "https://casten.house.gov"},
    "Danny Davis": {"name": "Danny Davis", "state": "Illinois", "district": "7", "party": "Democrat", "website": "https://davisdanny.house.gov"},
    "Raja Krishnamoorthi": {"name": "Raja Krishnamoorthi", "state": "Illinois", "district": "8", "party": "Democrat", "website": "https://krishnamoorthi.house.gov"},
    "Jan Schakowsky": {"name": "Jan Schakowsky", "state": "Illinois", "district": "9", "party": "Democrat", "website": "https://schakowsky.house.gov"},
    "Brad Schneider": {"name": "Brad Schneider", "state": "Illinois", "district": "10", "party": "Democrat", "website": "https://schneider.house.gov"},
    "Bill Foster": {"name": "Bill Foster", "state": "Illinois", "district": "11", "party": "Democrat", "website": "https://foster.house.gov"},
    "Mike Bost": {"name": "Mike Bost", "state": "Illinois", "district": "12", "party": "Republican", "website": "https://bost.house.gov"},
    "Nikki Budzinski": {"name": "Nikki Budzinski", "state": "Illinois", "district": "13", "party": "Democrat", "website": "https://budzinski.house.gov"},
    "Lauren Underwood": {"name": "Lauren Underwood", "state": "Illinois", "district": "14", "party": "Democrat", "website": "https://underwood.house.gov"},
    "Mary Miller": {"name": "Mary Miller", "state": "Illinois", "district": "15", "party": "Republican", "website": "https://marymiller.house.gov"},
    "Darin LaHood": {"name": "Darin LaHood", "state": "Illinois", "district": "16", "party": "Republican", "website": "https://lahood.house.gov"},
    "Eric Sorensen": {"name": "Eric Sorensen", "state": "Illinois", "district": "17", "party": "Democrat", "website": "https://sorensen.house.gov"},
    "Frank Mrvan": {"name": "Frank Mrvan", "state": "Indiana", "district": "1", "party": "Democrat", "website": "https://mrvan.house.gov"},
    "Rudy Yakym": {"name": "Rudy Yakym", "state": "Indiana", "district": "2", "party": "Republican", "website": "https://yakym.house.gov"},
    "Jim Banks": {"name": "Jim Banks", "state": "Indiana", "district": "3", "party": "Republican", "website": "https://banks.house.gov"},
    "Jim Baird": {"name": "Jim Baird", "state": "Indiana", "district": "4", "party": "Republican", "website": "https://baird.house.gov"},
    "Victoria Spartz": {"name": "Victoria Spartz", "state": "Indiana", "district": "5", "party": "Republican", "website": "https://spartz.house.gov"},
    "Greg Pence": {"name": "Greg Pence", "state": "Indiana", "district": "6", "party": "Republican", "website": "https://pence.house.gov"},
    "André Carson": {"name": "André Carson", "state": "Indiana", "district": "7", "party": "Democrat", "website": "https://carson.house.gov"},
    "Larry Bucshon": {"name": "Larry Bucshon", "state": "Indiana", "district": "8", "party": "Republican", "website": "https://bucshon.house.gov"},
    "Erin Houchin": {"name": "Erin Houchin", "state": "Indiana", "district": "9", "party": "Republican", "website": "https://houchin.house.gov"},
    "Mariannette Miller-Meeks": {"name": "Mariannette Miller-Meeks", "state": "Iowa", "district": "1", "party": "Republican", "website": "https://millermeeks.house.gov"},
    "Ashley Hinson": {"name": "Ashley Hinson", "state": "Iowa", "district": "2", "party": "Republican", "website": "https://hinson.house.gov"},
    "Zach Nunn": {"name": "Zach Nunn", "state": "Iowa", "district": "3", "party": "Republican", "website": "https://nunn.house.gov"},
    "Randy Feenstra": {"name": "Randy Feenstra", "state": "Iowa", "district": "4", "party": "Republican", "website": "https://feenstra.house.gov"},
    "Tracy Mann": {"name": "Tracy Mann", "state": "Kansas", "district": "1", "party": "Republican", "website": "https://mann.house.gov"},
    "Jake LaTurner": {"name": "Jake LaTurner", "state": "Kansas", "district": "2", "party": "Republican", "website": "https://laturner.house.gov"},
    "Sharice Davids": {"name": "Sharice Davids", "state": "Kansas", "district": "3", "party": "Democrat", "website": "https://davids.house.gov"},
    "Ron Estes": {"name": "Ron Estes", "state": "Kansas", "district": "4", "party": "Republican", "website": "https://estes.house.gov"},
    "James Comer": {"name": "James Comer", "state": "Kentucky", "district": "1", "party": "Republican", "website": "https://comer.house.gov"},
    "Brett Guthrie": {"name": "Brett Guthrie", "state": "Kentucky", "district": "2", "party": "Republican", "website": "https://guthrie.house.gov"},
    "Morgan McGarvey": {"name": "Morgan McGarvey", "state": "Kentucky", "district": "3", "party": "Democrat", "website": "https://mcgarvey.house.gov"},
    "Thomas Massie": {"name": "Thomas Massie", "state": "Kentucky", "district": "4", "party": "Republican", "website": "https://massie.house.gov"},
    "Harold Rogers": {"name": "Harold Rogers", "state": "Kentucky", "district": "5", "party": "Republican", "website": "https://halrogers.house.gov"},
    "Andy Barr": {"name": "Andy Barr", "state": "Kentucky", "district": "6", "party": "Republican", "website": "https://barr.house.gov"},
    "Steve Scalise": {"name": "Steve Scalise", "state": "Louisiana", "district": "1", "party": "Republican", "website": "https://scalise.house.gov"},
    "Troy Carter": {"name": "Troy Carter", "state": "Louisiana", "district": "2", "party": "Democrat", "website": "https://carter.house.gov"},
    "Clay Higgins": {"name": "Clay Higgins", "state": "Louisiana", "district": "3", "party": "Republican", "website": "https://higgins.house.gov"},
    "Mike Johnson": {"name": "Mike Johnson", "state": "Louisiana", "district": "4", "party": "Republican", "website": "https://mikejohnson.house.gov"},
    "Julia Letlow": {"name": "Julia Letlow", "state": "Louisiana", "district": "5", "party": "Republican", "website": "https://letlow.house.gov"},
    "Garret Graves": {"name": "Garret Graves", "state": "Louisiana", "district": "6", "party": "Republican", "website": "https://graves.house.gov"},
    "Chellie Pingree": {"name": "Chellie Pingree", "state": "Maine", "district": "1", "party": "Democrat", "website": "https://pingree.house.gov"},
    "Jared Golden": {"name": "Jared Golden", "state": "Maine", "district": "2", "party": "Democrat", "website": "https://golden.house.gov"},
    "Andy Harris": {"name": "Andy Harris", "state": "Maryland", "district": "1", "party": "Republican", "website": "https://harris.house.gov"},
    "Dutch Ruppersberger": {"name": "Dutch Ruppersberger", "state": "Maryland", "district": "2", "party": "Democrat", "website": "https://ruppersberger.house.gov"},
    "John Sarbanes": {"name": "John Sarbanes", "state": "Maryland", "district": "3", "party": "Democrat", "website": "https://sarbanes.house.gov"},
    "Glenn Ivey": {"name": "Glenn Ivey", "state": "Maryland", "district": "4", "party": "Democrat", "website": "https://ivey.house.gov"},
    "Steny Hoyer": {"name": "Steny Hoyer", "state": "Maryland", "district": "5", "party": "Democrat", "website": "https://hoyer.house.gov"},
    "David Trone": {"name": "David Trone", "state": "Maryland", "district": "6", "party": "Democrat", "website": "https://trone.house.gov"},
    "Kweisi Mfume": {"name": "Kweisi Mfume", "state": "Maryland", "district": "7", "party": "Democrat", "website": "https://mfume.house.gov"},
    "Jamie Raskin": {"name": "Jamie Raskin", "state": "Maryland", "district": "8", "party": "Democrat", "website": "https://raskin.house.gov"},
    "Richard Neal": {"name": "Richard Neal", "state": "Massachusetts", "district": "1", "party": "Democrat", "website": "https://neal.house.gov"},
    "Jim McGovern": {"name": "Jim McGovern", "state": "Massachusetts", "district": "2", "party": "Democrat", "website": "https://mcgovern.house.gov"},
    "Lori Trahan": {"name": "Lori Trahan", "state": "Massachusetts", "district": "3", "party": "Democrat", "website": "https://trahan.house.gov"},
    "Jake Auchincloss": {"name": "Jake Auchincloss", "state": "Massachusetts", "district": "4", "party": "Democrat", "website": "https://auchincloss.house.gov"},
    "Katherine Clark": {"name": "Katherine Clark", "state": "Massachusetts", "district": "5", "party": "Democrat", "website": "https://katherineclark.house.gov"},
    "Seth Moulton": {"name": "Seth Moulton", "state": "Massachusetts", "district": "6", "party": "Democrat", "website": "https://moulton.house.gov"},
    "Ayanna Pressley": {"name": "Ayanna Pressley", "state": "Massachusetts", "district": "7", "party": "Democrat", "website": "https://pressley.house.gov"},
    "Stephen Lynch": {"name": "Stephen Lynch", "state": "Massachusetts", "district": "8", "party": "Democrat", "website": "https://lynch.house.gov"},
    "Bill Keating": {"name": "Bill Keating", "state": "Massachusetts", "district": "9", "party": "Democrat", "website": "https://keating.house.gov"},
    "Jack Bergman": {"name": "Jack Bergman", "state": "Michigan", "district": "1", "party": "Republican", "website": "https://bergman.house.gov"},
    "John Moolenaar": {"name": "John Moolenaar", "state": "Michigan", "district": "2", "party": "Republican", "website": "https://moolenaar.house.gov"},
    "Hillary Scholten": {"name": "Hillary Scholten", "state": "Michigan", "district": "3", "party": "Democrat", "website": "https://scholten.house.gov"},
    "Bill Huizenga": {"name": "Bill Huizenga", "state": "Michigan", "district": "4", "party": "Republican", "website": "https://huizenga.house.gov"},
    "Tim Walberg": {"name": "Tim Walberg", "state": "Michigan", "district": "5", "party": "Republican", "website": "https://walberg.house.gov"},
    "Debbie Dingell": {"name": "Debbie Dingell", "state": "Michigan", "district": "6", "party": "Democrat", "website": "https://dingell.house.gov"},
    "Elissa Slotkin": {"name": "Elissa Slotkin", "state": "Michigan", "district": "7", "party": "Democrat", "website": "https://slotkin.house.gov"},
    "Dan Kildee": {"name": "Dan Kildee", "state": "Michigan", "district": "8", "party": "Democrat", "website": "https://dankildee.house.gov"},
    "Lisa McClain": {"name": "Lisa McClain", "state": "Michigan", "district": "9", "party": "Republican", "website": "https://mcclain.house.gov"},
    "John James": {"name": "John James", "state": "Michigan", "district": "10", "party": "Republican", "website": "https://james.house.gov"},
    "Haley Stevens": {"name": "Haley Stevens", "state": "Michigan", "district": "11", "party": "Democrat", "website": "https://stevens.house.gov"},
    "Rashida Tlaib": {"name": "Rashida Tlaib", "state": "Michigan", "district": "12", "party": "Democrat", "website": "https://tlaib.house.gov"},
    "Shri Thanedar": {"name": "Shri Thanedar", "state": "Michigan", "district": "13", "party": "Democrat", "website": "https://thanedar.house.gov"},
    "Brad Finstad": {"name": "Brad Finstad", "state": "Minnesota", "district": "1", "party": "Republican", "website": "https://finstad.house.gov"},
    "Angie Craig": {"name": "Angie Craig", "state": "Minnesota", "district": "2", "party": "Democrat", "website": "https://craig.house.gov"},
    "Dean Phillips": {"name": "Dean Phillips", "state": "Minnesota", "district": "3", "party": "Democrat", "website": "https://phillips.house.gov"},
    "Betty McCollum": {"name": "Betty McCollum", "state": "Minnesota", "district": "4", "party": "Democrat", "website": "https://mccollum.house.gov"},
    "Ilhan Omar": {"name": "Ilhan Omar", "state": "Minnesota", "district": "5", "party": "Democrat", "website": "https://omar.house.gov"},
    "Tom Emmer": {"name": "Tom Emmer", "state": "Minnesota", "district": "6", "party": "Republican", "website": "https://emmer.house.gov"},
    "Michelle Fischbach": {"name": "Michelle Fischbach", "state": "Minnesota", "district": "7", "party": "Republican", "website": "https://fischbach.house.gov"},
    "Pete Stauber": {"name": "Pete Stauber", "state": "Minnesota", "district": "8", "party": "Republican", "website": "https://stauber.house.gov"},
    "Trent Kelly": {"name": "Trent Kelly", "state": "Mississippi", "district": "1", "party": "Republican", "website": "https://trentkelly.house.gov"},
    "Bennie Thompson": {"name": "Bennie Thompson", "state": "Mississippi", "district": "2", "party": "Democrat", "website": "https://benniethompson.house.gov"},
    "Michael Guest": {"name": "Michael Guest", "state": "Mississippi", "district": "3", "party": "Republican", "website": "https://guest.house.gov"},
    "Mike Ezell": {"name": "Mike Ezell", "state": "Mississippi", "district": "4", "party": "Republican", "website": "https://ezell.house.gov"},
    "Cori Bush": {"name": "Cori Bush", "state": "Missouri", "district": "1", "party": "Democrat", "website": "https://bush.house.gov"},
    "Ann Wagner": {"name": "Ann Wagner", "state": "Missouri", "district": "2", "party": "Republican", "website": "https://wagner.house.gov"},
    "Blaine Luetkemeyer": {"name": "Blaine Luetkemeyer", "state": "Missouri", "district": "3", "party": "Republican", "website": "https://luetkemeyer.house.gov"},
    "Mark Alford": {"name": "Mark Alford", "state": "Missouri", "district": "4", "party": "Republican", "website": "https://alford.house.gov"},
    "Emanuel Cleaver": {"name": "Emanuel Cleaver", "state": "Missouri", "district": "5", "party": "Democrat", "website": "https://cleaver.house.gov"},
    "Sam Graves": {"name": "Sam Graves", "state": "Missouri", "district": "6", "party": "Republican", "website": "https://graves.house.gov"},
    "Eric Burlison": {"name": "Eric Burlison", "state": "Missouri", "district": "7", "party": "Republican", "website": "https://burlison.house.gov"},
    "Jason Smith": {"name": "Jason Smith", "state": "Missouri", "district": "8", "party": "Republican", "website": "https://jasonsmith.house.gov"}, # Corrected website
    "Ryan Zinke": {"name": "Ryan Zinke", "state": "Montana", "district": "1", "party": "Republican", "website": "https://zinke.house.gov"},
    "Matt Rosendale": {"name": "Matt Rosendale", "state": "Montana", "district": "2", "party": "Republican", "website": "https://rosendale.house.gov"},
    "Mike Flood": {"name": "Mike Flood", "state": "Nebraska", "district": "1", "party": "Republican", "website": "https://flood.house.gov"},
    "Don Bacon": {"name": "Don Bacon", "state": "Nebraska", "district": "2", "party": "Republican", "website": "https://bacon.house.gov"},
    "Adrian Smith": {"name": "Adrian Smith", "state": "Nebraska", "district": "3", "party": "Republican", "website": "https://adriansmith.house.gov"},
    "Dina Titus": {"name": "Dina Titus", "state": "Nevada", "district": "1", "party": "Democrat", "website": "https://titus.house.gov"},
    "Mark Amodei": {"name": "Mark Amodei", "state": "Nevada", "district": "2", "party": "Republican", "website": "https://amodei.house.gov"},
    "Susie Lee": {"name": "Susie Lee", "state": "Nevada", "district": "3", "party": "Democrat", "website": "https://susielee.house.gov"},
    "Steven Horsford": {"name": "Steven Horsford", "state": "Nevada", "district": "4", "party": "Democrat", "website": "https://horsford.house.gov"},
    "Chris Pappas": {"name": "Chris Pappas", "state": "New Hampshire", "district": "1", "party": "Democrat", "website": "https://pappas.house.gov"},
    "Ann Kuster": {"name": "Ann Kuster", "state": "New Hampshire", "district": "2", "party": "Democrat", "website": "https://kuster.house.gov"},
    "Donald Norcross": {"name": "Donald Norcross", "state": "New Jersey", "district": "1", "party": "Democrat", "website": "https://norcross.house.gov"},
    "Jeff Van Drew": {"name": "Jeff Van Drew", "state": "New Jersey", "district": "2", "party": "Republican", "website": "https://vandrew.house.gov"},
    "Andy Kim": {"name": "Andy Kim", "state": "New Jersey", "district": "3", "party": "Democrat", "website": "https://kim.house.gov"},
    "Chris Smith": {"name": "Chris Smith", "state": "New Jersey", "district": "4", "party": "Republican", "website": "https://chrissmith.house.gov"},
    "Josh Gottheimer": {"name": "Josh Gottheimer", "state": "New Jersey", "district": "5", "party": "Democrat", "website": "https://gottheimer.house.gov"},
    "Frank Pallone": {"name": "Frank Pallone", "state": "New Jersey", "district": "6", "party": "Democrat", "website": "https://pallone.house.gov"},
    "Thomas Kean Jr.": {"name": "Thomas Kean Jr.", "state": "New Jersey", "district": "7", "party": "Republican", "website": "https://kean.house.gov"}, # Corrected name
    "Rob Menendez": {"name": "Rob Menendez", "state": "New Jersey", "district": "8", "party": "Democrat", "website": "https://menendez.house.gov"},
    "Bill Pascrell Jr.": {"name": "Bill Pascrell Jr.", "state": "New Jersey", "district": "9", "party": "Democrat", "website": "https://pascrell.house.gov"}, # Corrected name
    "Donald Payne Jr.": {"name": "Donald Payne Jr.", "state": "New Jersey", "district": "10", "party": "Democrat", "website": "https://payne.house.gov"}, # Corrected name
    "Mikie Sherrill": {"name": "Mikie Sherrill", "state": "New Jersey", "district": "11", "party": "Democrat", "website": "https://sherrill.house.gov"},
    "Bonnie Watson Coleman": {"name": "Bonnie Watson Coleman", "state": "New Jersey", "district": "12", "party": "Democrat", "website": "https://watsoncoleman.house.gov"},
    "Melanie Stansbury": {"name": "Melanie Stansbury", "state": "New Mexico", "district": "1", "party": "Democrat", "website": "https://stansbury.house.gov"},
    "Gabe Vasquez": {"name": "Gabe Vasquez", "state": "New Mexico", "district": "2", "party": "Democrat", "website": "https://vasquez.house.gov"},
    "Teresa Leger Fernandez": {"name": "Teresa Leger Fernandez", "state": "New Mexico", "district": "3", "party": "Democrat", "website": "https://legerfernandez.house.gov"},
    "Nick LaLota": {"name": "Nick LaLota", "state": "New York", "district": "1", "party": "Republican", "website": "https://lalota.house.gov/"},
    "Andrew Garbarino": {"name": "Andrew Garbarino", "state": "New York", "district": "2", "party": "Republican", "website": "https://garbarino.house.gov"},
    "George Santos": {"name": "George Santos", "state": "New York", "district": "3", "party": "Republican", "website": "https://santos.house.gov"},
    "Anthony D'Esposito": {"name": "Anthony D'Esposito", "state": "New York", "district": "4", "party": "Republican", "website": "https://desposito.house.gov"},
    "Gregory Meeks": {"name": "Gregory Meeks", "state": "New York", "district": "5", "party": "Democrat", "website": "https://meeks.house.gov"},
    "Grace Meng": {"name": "Grace Meng", "state": "New York", "district": "6", "party": "Democrat", "website": "https://meng.house.gov"},
    "Nydia Velázquez": {"name": "Nydia Velázquez", "state": "New York", "district": "7", "party": "Democrat", "website": "https://velazquez.house.gov"},
    "Hakeem Jeffries": {"name": "Hakeem Jeffries", "state": "New York", "district": "8", "party": "Democrat", "website": "https://jeffries.house.gov"},
    "Yvette Clarke": {"name": "Yvette Clarke", "state": "New York", "district": "9", "party": "Democrat", "website": "https://clarke.house.gov"},
    "Dan Goldman": {"name": "Dan Goldman", "state": "New York", "district": "10", "party": "Democrat", "website": "https://goldman.house.gov"},
    "Nicole Malliotakis": {"name": "Nicole Malliotakis", "state": "New York", "district": "11", "party": "Republican", "website": "https://malliotakis.house.gov"},
    "Jerry Nadler": {"name": "Jerry Nadler", "state": "New York", "district": "12", "party": "Democrat", "website": "https://nadler.house.gov"},
    "Adriano Espaillat": {"name": "Adriano Espaillat", "state": "New York", "district": "13", "party": "Democrat", "website": "https://espaillat.house.gov"},
    "Alexandria Ocasio-Cortez": {"name": "Alexandria Ocasio-Cortez", "state": "New York", "district": "14", "party": "Democrat", "website": "https://ocasio-cortez.house.gov/"},
    "Ritchie Torres": {"name": "Ritchie Torres", "state": "New York", "district": "15", "party": "Democrat", "website": "https://torres.house.gov"},
    "Jamaal Bowman": {"name": "Jamaal Bowman", "state": "New York", "district": "16", "party": "Democrat", "website": "https://bowman.house.gov"},
    "Mike Lawler": {"name": "Mike Lawler", "state": "New York", "district": "17", "party": "Republican", "website": "https://lawler.house.gov"},
    "Pat Ryan": {"name": "Pat Ryan", "state": "New York", "district": "18", "party": "Democrat", "website": "https://patryan.house.gov"},
    "Marc Molinaro": {"name": "Marc Molinaro", "state": "New York", "district": "19", "party": "Republican", "website": "https://molinaro.house.gov"},
    "Paul Tonko": {"name": "Paul Tonko", "state": "New York", "district": "20", "party": "Democrat", "website": "https://tonko.house.gov"},
    "Elise Stefanik": {"name": "Elise Stefanik", "state": "New York", "district": "21", "party": "Republican", "website": "https://stefanik.house.gov"},
    "Brandon Williams": {"name": "Brandon Williams", "state": "New York", "district": "22", "party": "Republican", "website": "https://williams.house.gov"},
    "Nick Langworthy": {"name": "Nick Langworthy", "state": "New York", "district": "23", "party": "Republican", "website": "https://langworthy.house.gov"},
    "Claudia Tenney": {"name": "Claudia Tenney", "state": "New York", "district": "24", "party": "Republican", "website": "https://tenney.house.gov"},
    "Joseph Morelle": {"name": "Joseph Morelle", "state": "New York", "district": "25", "party": "Democrat", "website": "https://morelle.house.gov"},
    "Brian Higgins": {"name": "Brian Higgins", "state": "New York", "district": "26", "party": "Democrat", "website": "https://higgins.house.gov/"},
    "Don Davis": {"name": "Don Davis", "state": "North Carolina", "district": "1", "party": "Democrat", "website": "https://dondavis.house.gov/"},
    "Deborah Ross": {"name": "Deborah Ross", "state": "North Carolina", "district": "2", "party": "Democrat", "website": "https://ross.house.gov"},
    "Greg Murphy": {"name": "Greg Murphy", "state": "North Carolina", "district": "3", "party": "Republican", "website": "https://murphy.house.gov"},
    "Valerie Foushee": {"name": "Valerie Foushee", "state": "North Carolina", "district": "4", "party": "Democrat", "website": "https://foushee.house.gov"},
    "Virginia Foxx": {"name": "Virginia Foxx", "state": "North Carolina", "district": "5", "party": "Republican", "website": "https://foxx.house.gov"},
    "Kathy Manning": {"name": "Kathy Manning", "state": "North Carolina", "district": "6", "party": "Democrat", "website": "https://manning.house.gov"},
    "David Rouzer": {"name": "David Rouzer", "state": "North Carolina", "district": "7", "party": "Republican", "website": "https://rouzer.house.gov"},
    "Dan Bishop": {"name": "Dan Bishop", "state": "North Carolina", "district": "8", "party": "Republican", "website": "https://danbishop.house.gov"},
    "Richard Hudson": {"name": "Richard Hudson", "state": "North Carolina", "district": "9", "party": "Republican", "website": "https://hudson.house.gov"},
    "Patrick McHenry": {"name": "Patrick McHenry", "state": "North Carolina", "district": "10", "party": "Republican", "website": "https://mchenry.house.gov"},
    "Chuck Edwards": {"name": "Chuck Edwards", "state": "North Carolina", "district": "11", "party": "Republican", "website": "https://edwards.house.gov"},
    "Alma Adams": {"name": "Alma Adams", "state": "North Carolina", "district": "12", "party": "Democrat", "website": "https://adams.house.gov"},
    "Wiley Nickel": {"name": "Wiley Nickel", "state": "North Carolina", "district": "13", "party": "Democrat", "website": "https://nickel.house.gov"},
    "Jeff Jackson": {"name": "Jeff Jackson", "state": "North Carolina", "district": "14", "party": "Democrat", "website": "https://jeffjackson.house.gov"},
    "Kelly Armstrong": {"name": "Kelly Armstrong", "state": "North Dakota", "district": "At-Large", "party": "Republican", "website": "https://armstrong.house.gov"},
    "Greg Landsman": {"name": "Greg Landsman", "state": "Ohio", "district": "1", "party": "Democrat", "website": "https://landsman.house.gov"},
    "Brad Wenstrup": {"name": "Brad Wenstrup", "state": "Ohio", "district": "2", "party": "Republican", "website": "https://wenstrup.house.gov"},
    "Joyce Beatty": {"name": "Joyce Beatty", "state": "Ohio", "district": "3", "party": "Democrat", "website": "https://beatty.house.gov"},
    "Jim Jordan": {"name": "Jim Jordan", "state": "Ohio", "district": "4", "party": "Republican", "website": "https://jordan.house.gov"},
    "Bob Latta": {"name": "Bob Latta", "state": "Ohio", "district": "5", "party": "Republican", "website": "https://latta.house.gov"},
    "Bill Johnson": {"name": "Bill Johnson", "state": "Ohio", "district": "6", "party": "Republican", "website": "https://billjohnson.house.gov"},
    "Max Miller": {"name": "Max Miller", "state": "Ohio", "district": "7", "party": "Republican", "website": "https://maxmiller.house.gov"},
    "Warren Davidson": {"name": "Warren Davidson", "state": "Ohio", "district": "8", "party": "Republican", "website": "https://davidson.house.gov"},
    "Marcy Kaptur": {"name": "Marcy Kaptur", "state": "Ohio", "district": "9", "party": "Democrat", "website": "https://kaptur.house.gov"},
    "Mike Turner": {"name": "Mike Turner", "state": "Ohio", "district": "10", "party": "Republican", "website": "https://turner.house.gov"},
    "Shontel Brown": {"name": "Shontel Brown", "state": "Ohio", "district": "11", "party": "Democrat", "website": "https://brown.house.gov"},
    "Troy Balderson": {"name": "Troy Balderson", "state": "Ohio", "district": "12", "party": "Republican", "website": "https://balderson.house.gov"},
    "Emilia Sykes": {"name": "Emilia Sykes", "state": "Ohio", "district": "13", "party": "Democrat", "website": "https://sykes.house.gov"},
    "David Joyce": {"name": "David Joyce", "state": "Ohio", "district": "14", "party": "Republican", "website": "https://joyce.house.gov"},
    "Mike Carey": {"name": "Mike Carey", "state": "Ohio", "district": "15", "party": "Republican", "website": "https://carey.house.gov"},
    "Kevin Hern": {"name": "Kevin Hern", "state": "Oklahoma", "district": "1", "party": "Republican", "website": "https://hern.house.gov/"},
    "Josh Brecheen": {"name": "Josh Brecheen", "state": "Oklahoma", "district": "2", "party": "Republican", "website": "https://brecheen.house.gov/"},
    "Frank Lucas": {"name": "Frank Lucas", "state": "Oklahoma", "district": "3", "party": "Republican", "website": "https://lucas.house.gov"},
    "Tom Cole": {"name": "Tom Cole", "state": "Oklahoma", "district": "4", "party": "Republican", "website": "https://cole.house.gov"},
    "Stephanie Bice": {"name": "Stephanie Bice", "state": "Oklahoma", "district": "5", "party": "Republican", "website": "https://bice.house.gov"},
    "Suzanne Bonamici": {"name": "Suzanne Bonamici", "state": "Oregon", "district": "1", "party": "Democrat", "website": "https://bonamici.house.gov"},
    "Cliff Bentz": {"name": "Cliff Bentz", "state": "Oregon", "district": "2", "party": "Republican", "website": "https://bentz.house.gov"},
    "Earl Blumenauer": {"name": "Earl Blumenauer", "state": "Oregon", "district": "3", "party": "Democrat", "website": "https://blumenauer.house.gov"},
    "Val Hoyle": {"name": "Val Hoyle", "state": "Oregon", "district": "4", "party": "Democrat", "website": "https://hoyle.house.gov"},
    "Lori Chavez-DeRemer": {"name": "Lori Chavez-DeRemer", "state": "Oregon", "district": "5", "party": "Republican", "website": "https://chavez-deremer.house.gov"},
    "Andrea Salinas": {"name": "Andrea Salinas", "state": "Oregon", "district": "6", "party": "Democrat", "website": "https://salinas.house.gov"},
    "Brian Fitzpatrick": {"name": "Brian Fitzpatrick", "state": "Pennsylvania", "district": "1", "party": "Republican", "website": "https://fitzpatrick.house.gov"},
    "Brendan Boyle": {"name": "Brendan Boyle", "state": "Pennsylvania", "district": "2", "party": "Democrat", "website": "https://boyle.house.gov"},
    "Dwight Evans": {"name": "Dwight Evans", "state": "Pennsylvania", "district": "3", "party": "Democrat", "website": "https://evans.house.gov"},
    "Madeleine Dean": {"name": "Madeleine Dean", "state": "Pennsylvania", "district": "4", "party": "Democrat", "website": "https://dean.house.gov"},
    "Mary Gay Scanlon": {"name": "Mary Gay Scanlon", "state": "Pennsylvania", "district": "5", "party": "Democrat", "website": "https://scanlon.house.gov"},
    "Chrissy Houlahan": {"name": "Chrissy Houlahan", "state": "Pennsylvania", "district": "6", "party": "Democrat", "website": "https://houlahan.house.gov"},
    "Susan Wild": {"name": "Susan Wild", "state": "Pennsylvania", "district": "7", "party": "Democrat", "website": "https://wild.house.gov"},
    "Matt Cartwright": {"name": "Matt Cartwright", "state": "Pennsylvania", "district": "8", "party": "Democrat", "website": "https://cartwright.house.gov"},
    "Dan Meuser": {"name": "Dan Meuser", "state": "Pennsylvania", "district": "9", "party": "Republican", "website": "https://meuser.house.gov"},
    "Scott Perry": {"name": "Scott Perry", "state": "Pennsylvania", "district": "10", "party": "Republican", "website": "https://perry.house.gov"},
    "Lloyd Smucker": {"name": "Lloyd Smucker", "state": "Pennsylvania", "district": "11", "party": "Republican", "website": "https://smucker.house.gov"},
    "Summer Lee": {"name": "Summer Lee", "state": "Pennsylvania", "district": "12", "party": "Democrat", "website": "https://summerlee.house.gov"},
    "John Joyce": {"name": "John Joyce", "state": "Pennsylvania", "district": "13", "party": "Republican", "website": "https://johnjoyce.house.gov"},
    "Guy Reschenthaler": {"name": "Guy Reschenthaler", "state": "Pennsylvania", "district": "14", "party": "Republican", "website": "https://reschenthaler.house.gov"},
    "Glenn Thompson": {"name": "Glenn Thompson", "state": "Pennsylvania", "district": "15", "party": "Republican", "website": "https://thompson.house.gov"},
    "Mike Kelly": {"name": "Mike Kelly", "state": "Pennsylvania", "district": "16", "party": "Republican", "website": "https://kelly.house.gov"},
    "Chris Deluzio": {"name": "Chris Deluzio", "state": "Pennsylvania", "district": "17", "party": "Democrat", "website": "https://deluzio.house.gov"},
    "David Cicilline": {"name": "David Cicilline", "state": "Rhode Island", "district": "1", "party": "Democrat", "website": "https://cicilline.house.gov/"},
    "Seth Magaziner": {"name": "Seth Magaziner", "state": "Rhode Island", "district": "2", "party": "Democrat", "website": "https://magaziner.house.gov"},
    "Nancy Mace": {"name": "Nancy Mace", "state": "South Carolina", "district": "1", "party": "Republican", "website": "https://mace.house.gov"},
    "Joe Wilson": {"name": "Joe Wilson", "state": "South Carolina", "district": "2", "party": "Republican", "website": "https://joewilson.house.gov"},
    "Jeff Duncan": {"name": "Jeff Duncan", "state": "South Carolina", "district": "3", "party": "Republican", "website": "https://jeffduncan.house.gov"},
    "William Timmons": {"name": "William Timmons", "state": "South Carolina", "district": "4", "party": "Republican", "website": "https://timmons.house.gov"},
    "Ralph Norman": {"name": "Ralph Norman", "state": "South Carolina", "district": "5", "party": "Republican", "website": "https://norman.house.gov"},
    "Jim Clyburn": {"name": "Jim Clyburn", "state": "South Carolina", "district": "6", "party": "Democrat", "website": "https://clyburn.house.gov"},
    "Russell Fry": {"name": "Russell Fry", "state": "South Carolina", "district": "7", "party": "Republican", "website": "https://fry.house.gov"},
    "Dusty Johnson": {"name": "Dusty Johnson", "state": "South Dakota", "district": "At-Large", "party": "Republican", "website": "https://dustyjohnson.house.gov"},
    "Diana Harshbarger": {"name": "Diana Harshbarger", "state": "Tennessee", "district": "1", "party": "Republican", "website": "https://harshbarger.house.gov"},
    "Tim Burchett": {"name": "Tim Burchett", "state": "Tennessee", "district": "2", "party": "Republican", "website": "https://burchett.house.gov"},
    "Chuck Fleischmann": {"name": "Chuck Fleischmann", "state": "Tennessee", "district": "3", "party": "Republican", "website": "https://fleischmann.house.gov"},
    "Scott DesJarlais": {"name": "Scott DesJarlais", "state": "Tennessee", "district": "4", "party": "Republican", "website": "https://desjarlais.house.gov"},
    "Andy Ogles": {"name": "Andy Ogles", "state": "Tennessee", "district": "5", "party": "Republican", "website": "https://ogles.house.gov"},
    "John Rose": {"name": "John Rose", "state": "Tennessee", "district": "6", "party": "Republican", "website": "https://johnrose.house.gov"},
    "Mark Green": {"name": "Mark Green", "state": "Tennessee", "district": "7", "party": "Republican", "website": "https://markgreen.house.gov"},
    "David Kustoff": {"name": "David Kustoff", "state": "Tennessee", "district": "8", "party": "Republican", "website": "https://kustoff.house.gov"},
    "Steve Cohen": {"name": "Steve Cohen", "state": "Tennessee", "district": "9", "party": "Democrat", "website": "https://cohen.house.gov"},
    "Nathaniel Moran": {"name": "Nathaniel Moran", "state": "Texas", "district": "1", "party": "Republican", "website": "https://moran.house.gov/"},
    "Dan Crenshaw": {"name": "Dan Crenshaw", "state": "Texas", "district": "2", "party": "Republican", "website": "https://crenshaw.house.gov/"},
    "Keith Self": {"name": "Keith Self", "state": "Texas", "district": "3", "party": "Republican", "website": "https://keithself.house.gov/"},
    "Pat Fallon": {"name": "Pat Fallon", "state": "Texas", "district": "4", "party": "Republican", "website": "https://fallon.house.gov/"},
    "Lance Gooden": {"name": "Lance Gooden", "state": "Texas", "district": "5", "party": "Republican", "website": "https://gooden.house.gov/"},
    "Jake Ellzey": {"name": "Jake Ellzey", "state": "Texas", "district": "6", "party": "Republican", "website": "https://ellzey.house.gov/"},
    "Lizzie Fletcher": {"name": "Lizzie Fletcher", "state": "Texas", "district": "7", "party": "Democrat", "website": "https://fletcher.house.gov/"},
    "Morgan Luttrell": {"name": "Morgan Luttrell", "state": "Texas", "district": "8", "party": "Republican", "website": "https://luttrell.house.gov"},
    "Al Green": {"name": "Al Green", "state": "Texas", "district": "9", "party": "Democrat", "website": "https://algreen.house.gov"},
    "Michael McCaul": {"name": "Michael McCaul", "state": "Texas", "district": "10", "party": "Republican", "website": "https://mccaul.house.gov"},
    "August Pfluger": {"name": "August Pfluger", "state": "Texas", "district": "11", "party": "Republican", "website": "https://pfluger.house.gov"},
    "Kay Granger": {"name": "Kay Granger", "state": "Texas", "district": "12", "party": "Republican", "website": "https://kaygranger.house.gov"},
    "Ronny Jackson": {"name": "Ronny Jackson", "state": "Texas", "district": "13", "party": "Republican", "website": "https://jackson.house.gov"},
    "Randy Weber": {"name": "Randy Weber", "state": "Texas", "district": "14", "party": "Republican", "website": "https://weber.house.gov"},
    "Monica De La Cruz": {"name": "Monica De La Cruz", "state": "Texas", "district": "15", "party": "Republican", "website": "https://delacruz.house.gov"},
    "Veronica Escobar": {"name": "Veronica Escobar", "state": "Texas", "district": "16", "party": "Democrat", "website": "https://escobar.house.gov"},
    "Pete Sessions": {"name": "Pete Sessions", "state": "Texas", "district": "17", "party": "Republican", "website": "https://sessions.house.gov"},
    "Sheila Jackson Lee": {"name": "Sheila Jackson Lee", "state": "Texas", "district": "18", "party": "Democrat", "website": "https://jacksonlee.house.gov"},
    "Jodey Arrington": {"name": "Jodey Arrington", "state": "Texas", "district": "19", "party": "Republican", "website": "https://arrington.house.gov/"},
    "Joaquin Castro": {"name": "Joaquin Castro", "state": "Texas", "district": "20", "party": "Democrat", "website": "https://castro.house.gov"},
    "Chip Roy": {"name": "Chip Roy", "state": "Texas", "district": "21", "party": "Republican", "website": "https://roy.house.gov"},
    "Troy Nehls": {"name": "Troy Nehls", "state": "Texas", "district": "22", "party": "Republican", "website": "https://nehls.house.gov/"},
    "Tony Gonzales": {"name": "Tony Gonzales", "state": "Texas", "district": "23", "party": "Republican", "website": "https://gonzales.house.gov"},
    "Beth Van Duyne": {"name": "Beth Van Duyne", "state": "Texas", "district": "24", "party": "Republican", "website": "https://vanduyne.house.gov"},
    "Roger Williams": {"name": "Roger Williams", "state": "Texas", "district": "25", "party": "Republican", "website": "https://williams.house.gov"},
    "Michael Burgess": {"name": "Michael Burgess", "state": "Texas", "district": "26", "party": "Republican", "website": "https://burgess.house.gov"},
    "Michael Cloud": {"name": "Michael Cloud", "state": "Texas", "district": "27", "party": "Republican", "website": "https://cloud.house.gov"},
    "Henry Cuellar": {"name": "Henry Cuellar", "state": "Texas", "district": "28", "party": "Democrat", "website": "https://cuellar.house.gov"},
    "Sylvia Garcia": {"name": "Sylvia Garcia", "state": "Texas", "district": "29", "party": "Democrat", "website": "https://sylviagarcia.house.gov"},
    "Jasmine Crockett": {"name": "Jasmine Crockett", "state": "Texas", "district": "30", "party": "Democrat", "website": "https://crockett.house.gov/"},
    "John Carter": {"name": "John Carter", "state": "Texas", "district": "31", "party": "Republican", "website": "https://carter.house.gov"},
    "Colin Allred": {"name": "Colin Allred", "state": "Texas", "district": "32", "party": "Democrat", "website": "https://allred.house.gov"},
    "Marc Veasey": {"name": "Marc Veasey", "state": "Texas", "district": "33", "party": "Democrat", "website": "https://veasey.house.gov"},
    "Vicente Gonzalez": {"name": "Vicente Gonzalez", "state": "Texas", "district": "34", "party": "Democrat", "website": "https://gonzalez.house.gov"},
    "Greg Casar": {"name": "Greg Casar", "state": "Texas", "district": "35", "party": "Democrat", "website": "https://casar.house.gov/"},
    "Brian Babin": {"name": "Brian Babin", "state": "Texas", "district": "36", "party": "Republican", "website": "https://babin.house.gov"},
    "Lloyd Doggett": {"name": "Lloyd Doggett", "state": "Texas", "district": "37", "party": "Democrat", "website": "https://doggett.house.gov/"},
    "Wesley Hunt": {"name": "Wesley Hunt", "state": "Texas", "district": "38", "party": "Republican", "website": "https://hunt.house.gov/"},
    "Blake Moore": {"name": "Blake Moore", "state": "Utah", "district": "1", "party": "Republican", "website": "https://blakemoore.house.gov"},
    "Celeste Maloy": {"name": "Celeste Maloy", "state": "Utah", "district": "2", "party": "Republican", "website": "https://maloy.house.gov/"},
    "John Curtis": {"name": "John Curtis", "state": "Utah", "district": "3", "party": "Republican", "website": "https://curtis.house.gov"},
    "Burgess Owens": {"name": "Burgess Owens", "state": "Utah", "district": "4", "party": "Republican", "website": "https://owens.house.gov"},
    "Becca Balint": {"name": "Becca Balint", "state": "Vermont", "district": "At-Large", "party": "Democrat", "website": "https://balint.house.gov"},
    "Rob Wittman": {"name": "Rob Wittman", "state": "Virginia", "district": "1", "party": "Republican", "website": "https://wittman.house.gov"},
    "Jen Kiggans": {"name": "Jen Kiggans", "state": "Virginia", "district": "2", "party": "Republican", "website": "https://kiggans.house.gov"},
    "Bobby Scott": {"name": "Bobby Scott", "state": "Virginia", "district": "3", "party": "Democrat", "website": "https://bobbyscott.house.gov"},
    "Jennifer McClellan": {"name": "Jennifer McClellan", "state": "Virginia", "district": "4", "party": "Democrat", "website": "https://mcclellan.house.gov"},
    "Bob Good": {"name": "Bob Good", "state": "Virginia", "district": "5", "party": "Republican", "website": "https://good.house.gov"},
    "Ben Cline": {"name": "Ben Cline", "state": "Virginia", "district": "6", "party": "Republican", "website": "https://cline.house.gov"},
    "Abigail Spanberger": {"name": "Abigail Spanberger", "state": "Virginia", "district": "7", "party": "Democrat", "website": "https://spanberger.house.gov"},
    "Don Beyer": {"name": "Don Beyer", "state": "Virginia", "district": "8", "party": "Democrat", "website": "https://beyer.house.gov"},
    "Morgan Griffith": {"name": "Morgan Griffith", "state": "Virginia", "district": "9", "party": "Republican", "website": "https://griffith.house.gov"},
    "Jennifer Wexton": {"name": "Jennifer Wexton", "state": "Virginia", "district": "10", "party": "Democrat", "website": "https://wexton.house.gov"},
    "Gerry Connolly": {"name": "Gerry Connolly", "state": "Virginia", "district": "11", "party": "Democrat", "website": "https://connolly.house.gov"},
    "Suzan DelBene": {"name": "Suzan DelBene", "state": "Washington", "district": "1", "party": "Democrat", "website": "https://delbene.house.gov/"},
    "Rick Larsen": {"name": "Rick Larsen", "state": "Washington", "district": "2", "party": "Democrat", "website": "https://larsen.house.gov/"},
    "Marie Gluesenkamp Perez": {"name": "Marie Gluesenkamp Perez", "state": "Washington", "district": "3", "party": "Democrat", "website": "https://gluesenkampperez.house.gov"},
    "Dan Newhouse": {"name": "Dan Newhouse", "state": "Washington", "district": "4", "party": "Republican", "website": "https://newhouse.house.gov"},
    "Cathy McMorris Rodgers": {"name": "Cathy McMorris Rodgers", "state": "Washington", "district": "5", "party": "Republican", "website": "https://mcmorrisrodgers.house.gov"},
    "Derek Kilmer": {"name": "Derek Kilmer", "state": "Washington", "district": "6", "party": "Democrat", "website": "https://kilmer.house.gov"},
    "Pramila Jayapal": {"name": "Pramila Jayapal", "state": "Washington", "district": "7", "party": "Democrat", "website": "https://jayapal.house.gov"},
    "Kim Schrier": {"name": "Kim Schrier", "state": "Washington", "district": "8", "party": "Democrat", "website": "https://schrier.house.gov"},
    "Adam Smith": {"name": "Adam Smith", "state": "Washington", "district": "9", "party": "Democrat", "website": "https://adamsmith.house.gov"},
    "Marilyn Strickland": {"name": "Marilyn Strickland", "state": "Washington", "district": "10", "party": "Democrat", "website": "https://strickland.house.gov"},
    "Carol Miller": {"name": "Carol Miller", "state": "West Virginia", "district": "1", "party": "Republican", "website": "https://miller.house.gov"},
    "Alex Mooney": {"name": "Alex Mooney", "state": "West Virginia", "district": "2", "party": "Republican", "website": "https://mooney.house.gov"},
    "Bryan Steil": {"name": "Bryan Steil", "state": "Wisconsin", "district": "1", "party": "Republican", "website": "https://steil.house.gov"},
    "Mark Pocan": {"name": "Mark Pocan", "state": "Wisconsin", "district": "2", "party": "Democrat", "website": "https://pocan.house.gov"},
    "Derrick Van Orden": {"name": "Derrick Van Orden", "state": "Wisconsin", "district": "3", "party": "Republican", "website": "https://vanorden.house.gov"},
    "Gwen Moore": {"name": "Gwen Moore", "state": "Wisconsin", "district": "4", "party": "Democrat", "website": "https://gwenmoore.house.gov"},
    "Scott Fitzgerald": {"name": "Scott Fitzgerald", "state": "Wisconsin", "district": "5", "party": "Republican", "website": "https://fitzgerald.house.gov"},
    "Glenn Grothman": {"name": "Glenn Grothman", "state": "Wisconsin", "district": "6", "party": "Republican", "website": "https://grothman.house.gov"},
    "Tom Tiffany": {"name": "Tom Tiffany", "state": "Wisconsin", "district": "7", "party": "Republican", "website": "https://tiffany.house.gov"},
    "Mike Gallagher": {"name": "Mike Gallagher", "state": "Wisconsin", "district": "8", "party": "Republican", "website": "https://gallagher.house.gov/"},
    "Harriet Hageman": {"name": "Harriet Hageman", "state": "Wyoming", "district": "At-Large", "party": "Republican", "website": "https://hageman.house.gov"},
    # Keep outdated/mismatched entries from original core.py marked as Unknown or with WDOD party if applicable
    "Conor Lamb": {"name": "Conor Lamb", "state": "California", "district": "22", "website": "https://lamb.house.gov", "party": "Unknown"},
    "Randy Neugebauer": {"name": "Randy Neugebauer", "state": "Texas", "district": "19", "website": "https://neugebauer.house.gov", "party": "Unknown"},
    "Eddie Bernice Johnson": {"name": "Eddie Bernice Johnson", "state": "Texas", "district": "30", "website": "https://ebjohnson.house.gov", "party": "Democrat"}, # Retired, kept party from WDOD source
    "Chris Stewart": {"name": "Chris Stewart", "state": "Utah", "district": "2", "website": "https://stewart.house.gov", "party": "Republican"}, # Resigned, kept party
}


sen_info = {
    "Tommy Tuberville": {"name": "Tommy Tuberville", "state": "Alabama", "party": "Republican", "website": "https://www.tuberville.senate.gov"},
    "Katie Boyd Britt": {"name": "Katie Boyd Britt", "state": "Alabama", "party": "Republican", "website": "https://www.britt.senate.gov"},
    "Lisa Murkowski": {"name": "Lisa Murkowski", "state": "Alaska", "party": "Republican", "website": "https://www.murkowski.senate.gov"},
    "Dan Sullivan": {"name": "Dan Sullivan", "state": "Alaska", "party": "Republican", "website": "https://www.sullivan.senate.gov"},
    "Mark Kelly": {"name": "Mark Kelly", "state": "Arizona", "party": "Democrat", "website": "https://www.kelly.senate.gov"},
    "Kyrsten Sinema": {"name": "Kyrsten Sinema", "state": "Arizona", "party": "Independent", "website": "https://www.sinema.senate.gov"},
    "John Boozman": {"name": "John Boozman", "state": "Arkansas", "party": "Republican", "website": "https://www.boozman.senate.gov"},
    "Tom Cotton": {"name": "Tom Cotton", "state": "Arkansas", "party": "Republican", "website": "https://www.cotton.senate.gov"},
    "Alex Padilla": {"name": "Alex Padilla", "state": "California", "party": "Democrat", "website": "https://www.padilla.senate.gov"},
    "Laphonza Butler": {"name": "Laphonza Butler", "state": "California", "party": "Democrat", "website": "https://www.butler.senate.gov"},
    "Michael Bennet": {"name": "Michael Bennet", "state": "Colorado", "party": "Democrat", "website": "https://www.bennet.senate.gov"},
    "John Hickenlooper": {"name": "John Hickenlooper", "state": "Colorado", "party": "Democrat", "website": "https://www.hickenlooper.senate.gov"},
    "Richard Blumenthal": {"name": "Richard Blumenthal", "state": "Connecticut", "party": "Democrat", "website": "https://www.blumenthal.senate.gov"},
    "Chris Murphy": {"name": "Chris Murphy", "state": "Connecticut", "party": "Democrat", "website": "https://www.murphy.senate.gov"},
    "Tom Carper": {"name": "Tom Carper", "state": "Delaware", "party": "Democrat", "website": "https://www.carper.senate.gov"},
    "Chris Coons": {"name": "Chris Coons", "state": "Delaware", "party": "Democrat", "website": "https://www.coons.senate.gov"},
    "Marco Rubio": {"name": "Marco Rubio", "state": "Florida", "party": "Republican", "website": "https://www.rubio.senate.gov"},
    "Rick Scott": {"name": "Rick Scott", "state": "Florida", "party": "Republican", "website": "https://www.rickscott.senate.gov"},
    "Jon Ossoff": {"name": "Jon Ossoff", "state": "Georgia", "party": "Democrat", "website": "https://www.ossoff.senate.gov"},
    "Raphael Warnock": {"name": "Raphael Warnock", "state": "Georgia", "party": "Democrat", "website": "https://www.warnock.senate.gov"},
    "Brian Schatz": {"name": "Brian Schatz", "state": "Hawaii", "party": "Democrat", "website": "https://www.schatz.senate.gov"},
    "Mazie Hirono": {"name": "Mazie Hirono", "state": "Hawaii", "party": "Democrat", "website": "https://www.hirono.senate.gov"},
    "Mike Crapo": {"name": "Mike Crapo", "state": "Idaho", "party": "Republican", "website": "https://www.crapo.senate.gov"},
    "Jim Risch": {"name": "Jim Risch", "state": "Idaho", "party": "Republican", "website": "https://www.risch.senate.gov"},
    "Dick Durbin": {"name": "Dick Durbin", "state": "Illinois", "party": "Democrat", "website": "https://www.durbin.senate.gov"},
    "Tammy Duckworth": {"name": "Tammy Duckworth", "state": "Illinois", "party": "Democrat", "website": "https://www.duckworth.senate.gov"},
    "Todd Young": {"name": "Todd Young", "state": "Indiana", "party": "Republican", "website": "https://www.young.senate.gov"},
    "Mike Braun": {"name": "Mike Braun", "state": "Indiana", "party": "Republican", "website": "https://www.braun.senate.gov"},
    "Chuck Grassley": {"name": "Chuck Grassley", "state": "Iowa", "party": "Republican", "website": "https://www.grassley.senate.gov"},
    "Joni Ernst": {"name": "Joni Ernst", "state": "Iowa", "party": "Republican", "website": "https://www.ernst.senate.gov"},
    "Jerry Moran": {"name": "Jerry Moran", "state": "Kansas", "party": "Republican", "website": "https://www.moran.senate.gov"},
    "Roger Marshall": {"name": "Roger Marshall", "state": "Kansas", "party": "Republican", "website": "https://www.marshall.senate.gov"},
    "Mitch McConnell": {"name": "Mitch McConnell", "state": "Kentucky", "party": "Republican", "website": "https://www.mcconnell.senate.gov"},
    "Rand Paul": {"name": "Rand Paul", "state": "Kentucky", "party": "Republican", "website": "https://www.paul.senate.gov"},
    "Bill Cassidy": {"name": "Bill Cassidy", "state": "Louisiana", "party": "Republican", "website": "https://www.cassidy.senate.gov"},
    "John Neely Kennedy": {"name": "John Neely Kennedy", "state": "Louisiana", "party": "Republican", "website": "https://www.kennedy.senate.gov"},
    "Susan Collins": {"name": "Susan Collins", "state": "Maine", "party": "Republican", "website": "https://www.collins.senate.gov"},
    "Angus King Jr.": {"name": "Angus King Jr.", "state": "Maine", "party": "Independent", "website": "https://www.king.senate.gov"},
    "Ben Cardin": {"name": "Ben Cardin", "state": "Maryland", "party": "Democrat", "website": "https://www.cardin.senate.gov"},
    "Chris Van Hollen": {"name": "Chris Van Hollen", "state": "Maryland", "party": "Democrat", "website": "https://www.vanhollen.senate.gov"},
    "Elizabeth Warren": {"name": "Elizabeth Warren", "state": "Massachusetts", "party": "Democrat", "website": "https://www.warren.senate.gov"},
    "Ed Markey": {"name": "Ed Markey", "state": "Massachusetts", "party": "Democrat", "website": "https://www.markey.senate.gov"},
    "Debbie Stabenow": {"name": "Debbie Stabenow", "state": "Michigan", "party": "Democrat", "website": "https://www.stabenow.senate.gov"},
    "Gary Peters": {"name": "Gary Peters", "state": "Michigan", "party": "Democrat", "website": "https://www.peters.senate.gov"},
    "Amy Klobuchar": {"name": "Amy Klobuchar", "state": "Minnesota", "party": "Democrat", "website": "https://www.klobuchar.senate.gov"},
    "Tina Smith": {"name": "Tina Smith", "state": "Minnesota", "party": "Democrat", "website": "https://www.smith.senate.gov"},
    "Roger Wicker": {"name": "Roger Wicker", "state": "Mississippi", "party": "Republican", "website": "https://www.wicker.senate.gov"},
    "Cindy Hyde-Smith": {"name": "Cindy Hyde-Smith", "state": "Mississippi", "party": "Republican", "website": "https://www.hydesmith.senate.gov"},
    "Josh Hawley": {"name": "Josh Hawley", "state": "Missouri", "party": "Republican", "website": "https://www.hawley.senate.gov"},
    "Eric Schmitt": {"name": "Eric Schmitt", "state": "Missouri", "party": "Republican", "website": "https://www.schmitt.senate.gov"},
    "Jon Tester": {"name": "Jon Tester", "state": "Montana", "party": "Democrat", "website": "https://www.tester.senate.gov"},
    "Steve Daines": {"name": "Steve Daines", "state": "Montana", "party": "Republican", "website": "https://www.daines.senate.gov"},
    "Deb Fischer": {"name": "Deb Fischer", "state": "Nebraska", "party": "Republican", "website": "https://www.fischer.senate.gov"},
    "Pete Ricketts": {"name": "Pete Ricketts", "state": "Nebraska", "party": "Republican", "website": "https://www.ricketts.senate.gov"},
    "Jacky Rosen": {"name": "Jacky Rosen", "state": "Nevada", "party": "Democrat", "website": "https://www.rosen.senate.gov"},
    "Catherine Cortez Masto": {"name": "Catherine Cortez Masto", "state": "Nevada", "party": "Democrat", "website": "https://www.cortezmasto.senate.gov"},
    "Jeanne Shaheen": {"name": "Jeanne Shaheen", "state": "New Hampshire", "party": "Democrat", "website": "https://www.shaheen.senate.gov"},
    "Maggie Hassan": {"name": "Maggie Hassan", "state": "New Hampshire", "party": "Democrat", "website": "https://www.hassan.senate.gov"},
    "Bob Menendez": {"name": "Bob Menendez", "state": "New Jersey", "party": "Democrat", "website": "https://www.menendez.senate.gov"},
    "Cory Booker": {"name": "Cory Booker", "state": "New Jersey", "party": "Democrat", "website": "https://www.booker.senate.gov"},
    "Martin Heinrich": {"name": "Martin Heinrich", "state": "New Mexico", "party": "Democrat", "website": "https://www.heinrich.senate.gov"},
    "Ben Ray Luján": {"name": "Ben Ray Luján", "state": "New Mexico", "party": "Democrat", "website": "https://www.lujan.senate.gov"},
    "Chuck Schumer": {"name": "Chuck Schumer", "state": "New York", "party": "Democrat", "website": "https://www.schumer.senate.gov"},
    "Kirsten Gillibrand": {"name": "Kirsten Gillibrand", "state": "New York", "party": "Democrat", "website": "https://www.gillibrand.senate.gov"},
    "Ted Budd": {"name": "Ted Budd", "state": "North Carolina", "party": "Republican", "website": "https://www.budd.senate.gov"},
    "Thom Tillis": {"name": "Thom Tillis", "state": "North Carolina", "party": "Republican", "website": "https://www.tillis.senate.gov"},
    "John Hoeven": {"name": "John Hoeven", "state": "North Dakota", "party": "Republican", "website": "https://www.hoeven.senate.gov"},
    "Kevin Cramer": {"name": "Kevin Cramer", "state": "North Dakota", "party": "Republican", "website": "https://www.cramer.senate.gov"},
    "Sherrod Brown": {"name": "Sherrod Brown", "state": "Ohio", "party": "Democrat", "website": "https://www.brown.senate.gov"},
    "J.D. Vance": {"name": "J.D. Vance", "state": "Ohio", "party": "Republican", "website": "https://www.vance.senate.gov"},
    "Markwayne Mullin": {"name": "Markwayne Mullin", "state": "Oklahoma", "party": "Republican", "website": "https://www.mullin.senate.gov"},
    "James Lankford": {"name": "James Lankford", "state": "Oklahoma", "party": "Republican", "website": "https://www.lankford.senate.gov"},
    "Ron Wyden": {"name": "Ron Wyden", "state": "Oregon", "party": "Democrat", "website": "https://www.wyden.senate.gov"},
    "Jeff Merkley": {"name": "Jeff Merkley", "state": "Oregon", "party": "Democrat", "website": "https://www.merkley.senate.gov"},
    "Robert Casey Jr.": {"name": "Robert Casey Jr.", "state": "Pennsylvania", "party": "Democrat", "website": "https://www.casey.senate.gov"},
    "John Fetterman": {"name": "John Fetterman", "state": "Pennsylvania", "party": "Democrat", "website": "https://www.fetterman.senate.gov"},
    "Jack Reed": {"name": "Jack Reed", "state": "Rhode Island", "party": "Democrat", "website": "https://www.reed.senate.gov"},
    "Sheldon Whitehouse": {"name": "Sheldon Whitehouse", "state": "Rhode Island", "party": "Democrat", "website": "https://www.whitehouse.senate.gov"},
    "Lindsey Graham": {"name": "Lindsey Graham", "state": "South Carolina", "party": "Republican", "website": "https://www.lgraham.senate.gov"},
    "Tim Scott": {"name": "Tim Scott", "state": "South Carolina", "party": "Republican", "website": "https://www.scott.senate.gov"},
    "John Thune": {"name": "John Thune", "state": "South Dakota", "party": "Republican", "website": "https://www.thune.senate.gov"},
    "Mike Rounds": {"name": "Mike Rounds", "state": "South Dakota", "party": "Republican", "website": "https://www.rounds.senate.gov"},
    "Marsha Blackburn": {"name": "Marsha Blackburn", "state": "Tennessee", "party": "Republican", "website": "https://www.blackburn.senate.gov"},
    "Bill Hagerty": {"name": "Bill Hagerty", "state": "Tennessee", "party": "Republican", "website": "https://www.hagerty.senate.gov"},
    "John Cornyn": {"name": "John Cornyn", "state": "Texas", "party": "Republican", "website": "https://www.cornyn.senate.gov"},
    "Ted Cruz": {"name": "Ted Cruz", "state": "Texas", "party": "Republican", "website": "https://www.cruz.senate.gov"},
    "Mitt Romney": {"name": "Mitt Romney", "state": "Utah", "party": "Republican", "website": "https://www.romney.senate.gov"},
    "Mike Lee": {"name": "Mike Lee", "state": "Utah", "party": "Republican", "website": "https://www.lee.senate.gov"},
    "Bernie Sanders": {"name": "Bernie Sanders", "state": "Vermont", "party": "Independent", "website": "https://www.sanders.senate.gov"},
    "Peter Welch": {"name": "Peter Welch", "state": "Vermont", "party": "Democrat", "website": "https://www.welch.senate.gov"},
    "Mark Warner": {"name": "Mark Warner", "state": "Virginia", "party": "Democrat", "website": "https://www.warner.senate.gov"},
    "Tim Kaine": {"name": "Tim Kaine", "state": "Virginia", "party": "Democrat", "website": "https://www.kaine.senate.gov"},
    "Patty Murray": {"name": "Patty Murray", "state": "Washington", "party": "Democrat", "website": "https://www.murray.senate.gov"},
    "Maria Cantwell": {"name": "Maria Cantwell", "state": "Washington", "party": "Democrat", "website": "https://www.cantwell.senate.gov"},
    "Joe Manchin": {"name": "Joe Manchin", "state": "West Virginia", "party": "Democrat", "website": "https://www.manchin.senate.gov"},
    "Shelley Moore Capito": {"name": "Shelley Moore Capito", "state": "West Virginia", "party": "Republican", "website": "https://www.capito.senate.gov"},
    "Tammy Baldwin": {"name": "Tammy Baldwin", "state": "Wisconsin", "party": "Democrat", "website": "https://www.baldwin.senate.gov"},
    "Ron Johnson": {"name": "Ron Johnson", "state": "Wisconsin", "party": "Republican", "website": "https://www.ronjohnson.senate.gov"},
    "John Barrasso": {"name": "John Barrasso", "state": "Wyoming", "party": "Republican", "website": "https://www.barrasso.senate.gov"},
    "Cynthia Lummis": {"name": "Cynthia Lummis", "state": "Wyoming", "party": "Republican", "website": "https://www.lummis.senate.gov"},
}

# Map for senator name variations between core.py and WDOD source
sen_name_map = {
    "John Kennedy": "John Neely Kennedy",
    "Angus King": "Angus King Jr.",
    "JD Vance": "J.D. Vance",
    "Bob Casey": "Robert Casey Jr."
}

# --- Function to Extract Python List Literal from Text ---
def extract_list_literal(file_content: str, list_variable_name: str) -> List[Dict[str, Any]]:
    """Extracts a list literal assigned to a variable from Python code text."""
    # Regex to find the list assignment, accounting for type hints
    # Matches 'variable_name: typehint = [' or 'variable_name = ['
    # Captures the content between the brackets []
    pattern = re.compile(
        rf"^{list_variable_name}(?::\s*\w+\[.*?\])?\s*=\s*\[(.*?)\]",
        re.DOTALL | re.MULTILINE
    )
    match = pattern.search(file_content)
    if not match:
        raise ValueError(f"Could not find list literal for '{list_variable_name}'")

    list_content = match.group(1).strip()
    # Need to evaluate this string as Python code to get the list object
    # This is generally unsafe with untrusted input, but here we trust core.py
    # We need a simple way to parse the dicts within the list string.
    # Using json.loads requires double quotes, so let's try replacing single quotes
    # Need to be careful with quotes within strings (e.g., D'Esposito)
    # A safer approach might be ast.literal_eval, but let's try eval first for simplicity here.
    # Ensure the environment for eval is controlled.
    try:
        # Replace Python comments within the list content
        list_content_no_comments = re.sub(r"#.*", "", list_content)
        # Attempt to evaluate the string as a Python list
        # WARNING: eval is risky. Use with caution.
        extracted_list = eval(f"[{list_content_no_comments}]", {"__builtins__": {}}, {})
        # Basic validation
        if not isinstance(extracted_list, list):
            raise TypeError("Extracted content is not a list")
        if extracted_list and not all(isinstance(item, dict) for item in extracted_list):
             raise TypeError("List items are not all dictionaries")
        return extracted_list
    except Exception as e:
        print(f"Error evaluating list literal for {list_variable_name}: {e}")
        # Fallback or safer parsing logic could go here (e.g., ast.literal_eval)
        # For now, re-raise the error
        raise

# --- Read Current Data from core.py ---
core_py_path = "backend/app/core.py"
try:
    with open(core_py_path, 'r', encoding='utf-8') as f:
        core_content = f.read()
except FileNotFoundError:
    print(f"Error: File not found at {core_py_path}")
    exit(1)
except Exception as e:
    print(f"Error reading {core_py_path}: {e}")
    exit(1)

try:
    representatives_raw = extract_list_literal(core_content, "representatives_raw")
    senators_raw = extract_list_literal(core_content, "senators_raw")
except Exception as e:
     print(f"Failed to parse lists from {core_py_path}. Error: {e}")
     print("Cannot proceed without the initial data.")
     exit(1)


# --- Update Logic ---

# Use dictionaries for easier updates and checking existence
# Start with existing core.py data
final_reps_dict = {rep['name']: rep for rep in representatives_raw}
final_sens_dict = {sen['name']: sen for sen in senators_raw}

# Add/Update Representatives from comprehensive WDOD info
for name, info in rep_info.items():
    # If rep exists in core data, just update party (and potentially other fields if needed)
    if name in final_reps_dict:
        final_reps_dict[name]['party'] = info.get('party', 'Unknown')
        # Optionally update other fields like website if WDOD source is more accurate
        if 'website' in info: final_reps_dict[name]['website'] = info['website']
        if 'district' in info: final_reps_dict[name]['district'] = info['district']
        if 'state' in info: final_reps_dict[name]['state'] = info['state']
    # If rep is completely new (wasn't in core.py data) add them
    else:
         # Only add if we have essential info
        if info.get('name') and info.get('state') and info.get('website'):
             final_reps_dict[name] = {
                 "name": info['name'],
                 "state": info['state'],
                 "district": info.get("district", "Unknown"), # Use unknown if district missing
                 "website": info['website'],
                 "party": info.get('party', 'Unknown')
            }

# Add/Update Senators from comprehensive WDOD info
for name, info in sen_info.items():
     # Handle potential name variations (e.g., Jr., middle names) for lookup
    core_match_name = sen_name_map.get(name, name) # Check if core.py used a different variation

    # If sen exists in core data (matching name or variation), update party
    if name in final_sens_dict or core_match_name in final_sens_dict:
        target_name = name if name in final_sens_dict else core_match_name
        final_sens_dict[target_name]['party'] = info.get('party', 'Unknown')
         # Optionally update other fields
        if 'website' in info: final_sens_dict[target_name]['website'] = info['website']
        if 'state' in info: final_sens_dict[target_name]['state'] = info['state']
    # If sen is completely new
    else:
         if info.get('name') and info.get('state') and info.get('website'):
            final_sens_dict[name] = {
                "name": info['name'],
                "state": info['state'],
                "website": info['website'],
                "party": info.get('party', 'Unknown')
            }


# Ensure party is set for any remaining members from original core list who weren't in WDOD info
for name, rep in final_reps_dict.items():
    if 'party' not in rep:
        rep['party'] = 'Unknown' # Or look up from another source if desired

for name, sen in final_sens_dict.items():
    if 'party' not in sen:
         sen['party'] = 'Unknown'


# Convert back to lists for the final output structure
updated_reps_raw_list = list(final_reps_dict.values())
updated_sens_raw_list = list(final_sens_dict.values())

# Sort by state then name for consistency (optional but helpful)
updated_reps_raw_list.sort(key=lambda x: (x['state'], x['name']))
updated_sens_raw_list.sort(key=lambda x: (x['state'], x['name']))


# --- Output for pasting into core.py ---

print("# --- Representatives Data ---")
print("representatives_raw: List[Dict[str, Any]] = [")
for i, rep in enumerate(updated_reps_raw_list):
    # Pretty print each dict entry using json.dumps for proper quoting
    # Ensure double quotes for JSON compatibility which Python dicts accept
    print(f"  {json.dumps(rep)}{',' if i < len(updated_reps_raw_list) - 1 else ''}")
print("]")

print("\n\n") # Separator

print("# --- Senators Data ---")
print("senators_raw: List[Dict[str, Any]] = [")
for i, sen in enumerate(updated_sens_raw_list):
    # Pretty print each dict entry
    print(f"  {json.dumps(sen)}{',' if i < len(updated_sens_raw_list) - 1 else ''}")
print("]")
