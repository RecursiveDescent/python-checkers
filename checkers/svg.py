import svgwrite
import checkers

import xml.etree.ElementTree as ET

crown = """<g transform="translate(CX, CY)"><g transform="matrix(SCALE,0,0,-SCALE,0,47.5)" id="g10"><g id="g12"><g clip-path="url(#clipPath16)" id="g14"><g transform="translate(19.9346,11.5146)" id="g20"><path id="path22" style="fill:#f4900c;fill-opacity:1;fill-rule:nonzero;stroke:none" d="m 0,0 c -0.517,-0.781 -1.353,-0.781 -1.869,0 l -4.678,5.071 c -0.516,0.782 -0.516,2.048 0,2.828 l 4.678,9.072 c 0.516,0.78 1.352,0.78 1.869,0 L 4.678,7.899 c 0.516,-0.78 0.516,-2.046 0,-2.828 L 0,0 Z"/></g><g transform="translate(29.4346,9.5146)" id="g24"><path id="path26" style="fill:#f4900c;fill-opacity:1;fill-rule:nonzero;stroke:none" d="m 0,0 c -0.517,-0.781 -1.353,-0.781 -1.869,0 l -4.678,5.071 c -0.516,0.782 -0.516,2.047 0,2.828 l 6.678,9.072 c 0.516,0.78 1.352,0.78 1.869,0 L 4.678,7.899 c 0.516,-0.781 0.516,-2.046 0,-2.828 L 0,0 Z"/></g><g transform="translate(10.4351,9.5146)" id="g28"><path id="path30" style="fill:#f4900c;fill-opacity:1;fill-rule:nonzero;stroke:none" d="m 0,0 c -0.517,-0.781 -1.354,-0.781 -1.871,0 l -4.677,5.071 c -0.516,0.782 -0.516,2.047 0,2.828 l 2.677,9.072 c 0.517,0.78 1.354,0.78 1.871,0 L 4.678,7.899 c 0.516,-0.781 0.516,-2.046 0,-2.828 L 0,0 Z"/></g><g transform="translate(34,26)" id="g32"><path id="path34" style="fill:#ffcc4d;fill-opacity:1;fill-rule:nonzero;stroke:none" d="m 0,0 c -0.45,-0.45 -2.12,-2.124 -4,-4.369 l -4.565,8.854 c -0.517,0.781 -1.353,0.781 -1.87,0 L -15,-4.368 -19.565,4.485 c -0.517,0.781 -1.354,0.781 -1.871,0 L -26,-4.368 c -1.88,2.245 -3.55,3.918 -4,4.368 -1,1 -2.485,0.94 -2,-1 1,-4 1,-7 1,-12 l 0,-2 c 0,-2.209 1.791,-4 4,-4 l 24,0 c 2.209,0 4,1.791 4,4 l 0,2 c 0,5 0,8 1,12 0.484,1.94 -1,2 -2,1"/></g><g transform="translate(22,15)" id="g36"><path id="path38" style="fill:#5c913b;fill-opacity:1;fill-rule:nonzero;stroke:none" d="m 0,0 c 0,-1.657 -1.343,-3 -3,-3 -1.657,0 -3,1.343 -3,3 0,1.657 1.343,3 3,3 1.657,0 3,-1.343 3,-3"/></g><g transform="translate(29,15)" id="g40"><path id="path42" style="fill:#5c913b;fill-opacity:1;fill-rule:nonzero;stroke:none" d="m 0,0 c 0,-1.104 -0.896,-2 -2,-2 -1.104,0 -2,0.896 -2,2 0,1.104 0.896,2 2,2 1.104,0 2,-0.896 2,-2"/></g><g transform="translate(36,15)" id="g44"><path id="path46" style="fill:#5c913b;fill-opacity:1;fill-rule:nonzero;stroke:none" d="m 0,0 c 0,-1.104 -0.896,-2 -2,-2 -1.104,0 -2,0.896 -2,2 0,1.104 0.896,2 2,2 1.104,0 2,-0.896 2,-2"/></g><g transform="translate(13,15)" id="g48"><path id="path50" style="fill:#5c913b;fill-opacity:1;fill-rule:nonzero;stroke:none" d="m 0,0 c 0,-1.104 -0.895,-2 -2,-2 -1.104,0 -2,0.896 -2,2 0,1.104 0.896,2 2,2 1.105,0 2,-0.896 2,-2"/></g><g transform="translate(6,15)" id="g52"><path id="path54" style="fill:#5c913b;fill-opacity:1;fill-rule:nonzero;stroke:none" d="m 0,0 c 0,-1.104 -0.895,-2 -2,-2 -1.104,0 -2,0.896 -2,2 0,1.104 0.896,2 2,2 1.105,0 2,-0.896 2,-2"/></g><g transform="translate(35,11)" id="g56"><path id="path58" style="fill:#ffac33;fill-opacity:1;fill-rule:nonzero;stroke:none" d="m 0,0 c 0,-2.209 -1.791,-4 -4,-4 l -24,0 c -2.209,0 -4,1.791 -4,4 L 0,0 Z"/></g></g></g></g></g>"""

class Wrapper(svgwrite.container.Group):
	def __init__(self, xml, **kwargs):
		self.xml = ET.fromstring(xml)

		self.elementname = "g"

		super().__init__(**kwargs)

	def get_xml(self):
		return self.xml

COLORS = {
	"black": "black",
	"black_border": "red",

	"red": "red",
	"red_border": "black",

	"light_square": "#ffce9e",
	"dark_square": "#d18b47",

	 "margin": "#212121",
	 "margin_text": "#e5e5e5"
}

def piece(piece, img = svgwrite.Drawing(size = (64, 64)), size = 64 * 1.5, center = None):
	base = size

	if not center:
		center = (base / 2, base / 2)
	
	# img = svgwrite.Drawing('test.svg', size=(base, base), profile='tiny')

	g = img.g()

	color = COLORS["red"] if piece.color == checkers.RED else COLORS["black"]

	border_color = COLORS["red_border"] if piece.color == checkers.RED else COLORS["black_border"]
	
	g.add(img.circle(center=(center[0], center[1]), r=base / 4, fill = border_color))

	g.add(img.circle(center=(center[0], center[1]), r=base / 4.5, fill = color))

	if piece.is_king:
		s = Wrapper(crown.replace("SCALE", str(0.8)).replace("CX", str(center[0] - 18 * 0.8)).replace("CY", str(center[1] - 40 * 0.8)))
		
		g.add(s)
	
	return g
	
def board(filename, board):
	img = svgwrite.Drawing(filename, size=(64 * 8 + 32, 64 * 8 + 32), profile='tiny')

	light = True

	img.add(img.rect(insert = (0, 0), size = (64 * 8 + 32, 64 * 8 + 32), fill = COLORS["margin"]))

	rows = "ABCDEFGH"

	coords_y = False

	for x in range(8):
		for y in range(8):
			flip = [*reversed([0,1,2,3,4,5,6,7])]
		
			cy = flip.index(y)

			if not coords_y:
				img.add(img.text(str(cy + 1), insert = (5, 50 + 64 * y), fill = COLORS["margin_text"]))
	
				img.add(img.text(str(cy + 1), insert = (16 + 64 * 8 + 5, 50 + 64 * y), fill = COLORS["margin_text"]))

			if y == 7:
				coords_y = True
			
			img.add(img.rect(insert = (x * 64 + 16, cy * 64 + 16), size = (64, 64), fill = (COLORS["light_square"] if light else COLORS["dark_square"])))

			if board.squares[checkers.SQUARES[rows[x] + str(y + 1)]] != checkers.EMPTY:
				square = board.squares[checkers.SQUARES[rows[x] + str(y + 1)]]
			
				piece = checkers.svg.piece(checkers.Piece(square & checkers.KING, square & checkers.RED), img, center = (x * 64 + 32 + 16, cy * 64 + 32 + 16))

				img.add(piece)

			light = not light

		img.add(img.text(rows[x].lower(), insert = (46 + 64 * x, 12), fill = COLORS["margin_text"], style = "font-family:\"Sans\""))

		img.add(img.text(rows[x].lower(), insert = (46 + 64 * x, 16 + 64 * 8 + 12), fill = COLORS["margin_text"], style = "font-family:\"Sans\""))

		light = not light

	img.save()
		

