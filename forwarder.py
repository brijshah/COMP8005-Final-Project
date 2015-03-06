
CFG_NAME: "forward.conf"

def main():
	routes = list[]
	for line in file(CFG_NAME):
		parts = line.split(":")
		routes.append((int(parts[0]), parts[1], int(parts[2])))
	print routes

if __name__ == '__main__':
	main()
