with open("regions.txt", 'r') as infile:
    with open("regions.csv", 'w') as outfile:
        game = ''
        region = ''
        for line in infile:
            line = line.strip()
            if line[:3] == "aaa":
                game = line[3:]
                continue
            if line[:3] == "bbb":
                region = line[3:]
                continue
            outfile.write(f"{game},{region},{line}\n")
