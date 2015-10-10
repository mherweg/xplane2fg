#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ac3d.py is part of osm2city.
"""

import string
import matplotlib.pyplot as plt
import logging
from pdb import pm
import numpy as np

from pyparsing import Literal, Word, quotedString, alphas, Optional, OneOrMore, \
    Group, ParseException, nums, Combine, Regex, alphanums, LineEnd, Each,\
    ParserElement, ZeroOrMore

#fmt_node = '%1.6f'
fmt_node = '%g'
fmt_surf = '%1.4g'

class Node(object):
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
    def __str__(self):
        return (fmt_node + ' ' + fmt_node + ' ' + fmt_node + '\n') % (self.x, self.y, self.z)

class Face(object):
    """if our texture is rotated in texture_atlas, set swap_uv=True"""
    def __init__(self, nodes_uv_list, typ, mat, swap_uv):
        assert len(nodes_uv_list) >= 2
        for n in nodes_uv_list:
            assert len(n) == 3
        if swap_uv:
            nodes_uv_list = [(n[0], n[2], n[1]) for n in nodes_uv_list]
        self.nodes_uv_list = nodes_uv_list
        self.typ = typ
        self.mat = mat

    def __str__(self):
        s = "SURF %s\n" % self.typ
        s += "mat %i\n" % self.mat
        s += "refs %i\n" % len(self.nodes_uv_list)
        s += string.join([("%i " + fmt_surf + " " + fmt_surf + "\n") % (n[0], n[1], n[2]) for n in self.nodes_uv_list], '')
        return s


class Object(object):
    """An object (3D) in an AC3D file with faces and nodes
       type:  
         The first 4 bits (flags & 0xF) is the type. 0 = polygon, 1 = closedline, 2 = line  
         The next four bits (flags >> 4) specify the shading and 
backface.  bit1 = shaded surface bit2 = twosided.
         ts0000
         31 
         268421
         0x20: two-sided poly
         0x00: single-sided poly
    """
    def __init__(self, name=None, stats=None, texture=None, texrep=None, texoff=None, rot=None, loc=None, crease=None, url=None, default_type=0x00, default_mat=0, default_swap_uv=False, kids=0):
        self._nodes = []
        self._faces = []
        self.name = name
        self.stats = stats
        self.texture = texture
        self.texrep = texrep
        self.texoff = texoff
        self.rot = rot
        self.loc = loc
        self.url = url
        self.crease = crease
        self.default_type = default_type
        self.default_mat = default_mat
        self.default_swap_uv = default_swap_uv
        self.kids = kids

    def close(self):
        pass

    def node(self, x, y, z):
        """Add new node. Return its index."""
        self._nodes.append(Node(x, y, z))
        if self.stats:
            self.stats.vertices += 1
        return len(self._nodes) - 1

    def nodes_as_array(self):
        """return all nodes as a numpy array"""
        return np.array([(n.x, n.y, n.z) for n in self._nodes])

    def next_node_index(self):
        return len(self._nodes)

    def total_nodes(self):
        return len(self._nodes)

    def total_faces(self):
        return len(self._faces)

    def face(self, nodes_uv_list, typ=None, mat=None, swap_uv=None):
        """Add new face. Return its index."""
        if not typ:
            typ = self.default_type
        if not mat:
            mat = self.default_mat
        if not swap_uv:
            swap_uv = self.default_swap_uv
        self._faces.append(Face(nodes_uv_list, typ, mat, swap_uv))
        if self.stats:
            self.stats.surfaces += 1
        return len(self._faces) - 1

    def is_empty(self):
        return not self._nodes

    def __str__(self):
        s = 'OBJECT poly\n'
        if self.name != None:
            s += 'name "%s"\n' % self.name
        if self.texrep != None:
            s += 'texrep %g %g\n' % (self.texrep[0], self.texrep[1])
        if self.texoff != None:
            s += 'texoff %g %g\n' % (self.texoff[0], self.texoff[1])
        if self.rot != None:
            s += 'rot %s\n' % string.join(["%g" % item for item in self.rot])
        if self.loc != None:
            s += 'loc %g %g %g\n' %  (self.loc[0], self.loc[1], self.loc[2])
        if self.crease != None:
            s += 'crease %g\n' % self.crease
        if self.url != None:
            s += 'url %s\n' % self.url
        if self.texture:
            s += 'texture "%s"\n' %self.texture
        s += 'numvert %i\n' % len(self._nodes)
        s += string.join([str(n) for n in self._nodes], '')
        s += 'numsurf %i\n' % len(self._faces)
        s += string.join([str(f) for f in self._faces], '')
        s += 'kids %i\n' % self.kids
        return s

    def plot(self):
        """note: here, Z is height."""
        for f in self._faces:
            X = [self._nodes[n[0]].x for n in f.nodes_uv_list]
            Y = [self._nodes[n[0]].z for n in f.nodes_uv_list]
            Z = [self._nodes[n[0]].y for n in f.nodes_uv_list]
            X.append(self._nodes[f.nodes_uv_list[0][0]].x)
            Y.append(self._nodes[f.nodes_uv_list[0][0]].z)
            #Z.append(self._nodes[f.nodes_uv_list[0][0]].y)
            #if max(Z) > 1.: break
            #print "MAX", max(Z)
            plt.plot(X, Y, '-o')
            for i in range(len(X)-1):
                x = 0.5*(X[i] + X[i+1])
                y = 0.5*(Y[i] + Y[i+1])
                plt.text(x+Z[i], y+Z[i], "%i" % i)

class Label(Object):
    def __init__(self):
        super(Label, self).__init__('label', texture='tex/ascii.png')
        self.char_w = 1.
        self.char_h = 1.

    def add(self, text, x, y, z, orientation=0, scale=1.):
        h = self.char_h * scale
        w = self.char_w * scale
        for c in str(text):
            code = ord(c) - 32
            if code < 0 or code > 126-32:
                logging.warning('Ignoring character %s' % c)
                continue
            cw = 1/95.
            u0 = code * cw - cw*0.05
            u1 = u0 + cw
            v0 = 0
            v1 = 1
            if 1 or orientation == 0:
                o = self.next_node_index()
                self.node(x, y, z)
                self.node(x, y, z+w)
                self.node(x+h, y, z+w)
                self.node(x+h, y, z)
                self.face([(o,  u0,v0),
                           (o+1,u1,v0),
                           (o+2,u1,v1),
                           (o+3,u0,v1)])
                z += w

class File(object):
    """
    Hold a number of 3D objects, each object consiting of nodes and faces.
    Either read objects from ac3d file or add them via new_object().
    Can write ac3d files.

    When adding objects, count nodes/surfaces etc internally, thereby eliminating
    a common source of bugs. Can also add 3d labels (useful for debugging, disabled
    by default)
    """
    def __init__(self, file_name = None, stats=None, show_labels = False):
        """Read ac3d data from file_name if given. Otherwise create empty ac3d object"""
        self.objects = []
        self.material_list = []
        self.show_labels = show_labels
        self.stats = stats
        self._current_object = None
        self.label_object = None
        self.texture_list = []
        if file_name != None:
            self.read(file_name)

    def new_object(self, name, texture, **kwargs):
        o = Object(name, self.stats, texture, **kwargs)
        self.objects.append(o)
        self._current_object = o
        return o

    def add_label(self, text, x, y, z, orientation=0, scale=1.):
        if not self.label_object:
            self.label_object = Label()
            if self.show_labels: self.objects.append(self.label_object)
        self.label_object.add(text, x, y, z, orientation, scale)
        return self.label_object

    def close_object(self):
        self._current_object.close()
        self._current_object = None

    def node(self, *args):
        return self._current_object.node(*args)

    def next_node_index(self):
        return self._current_object.next_node_index()

    def face(self, *args):
        return self._current_object.face(*args)

    def center(self):
        """translate all nodes such that the average is zero"""
        sum_x = sum_y = sum_z = n = 0
        for obj in self.objects:
            for node in obj._nodes:
                sum_x += node.x
                sum_y += node.y
                sum_z += node.z
                n += 1

        cx = float(sum_x) / n
        cy = float(sum_y) / n
        cz = float(sum_z) / n
        for obj in self.objects:
            for node in obj._nodes:
                node.x -= cx
                node.y -= cy
                node.z -= cz

    def total_nodes(self):
        """return total number of nodes of all objects"""
        return np.array([o.total_nodes() for o in self.objects]).sum()

    def total_faces(self):
        """return total number of faces of all objects"""
        return np.array([o.total_faces() for o in self.objects]).sum()

    def nodes_as_array(self):
        """return all nodes as a numpy array"""
        the_nodes = np.zeros((0,3))
        for o in self.objects:
            if o.is_empty(): continue
            a = o.nodes_as_array()
            the_nodes = np.vstack((the_nodes, a))
        return the_nodes

    def init_default_material(self):
        self.material_list.append('"default" rgb 1 1 1 amb 1 1 1 emis 0 0 0 spec 0.5 0.5 0.5 shi 64 trans 0')

    def add_material(self, the_mat):
        self.material_list.append(the_mat)

    def __str__(self):
        s = 'AC3Db\n'
        if self.material_list:
            s += string.join(['MATERIAL %s\n' % the_mat for the_mat in self.material_list], '')
        else:
            s += 'MATERIAL "" rgb 1 1 1 amb 1 1 1 emis 0 0 0 spec 0.5 0.5 0.5 shi 64 trans 0\n'
#        s += 'MATERIAL "" rgb 1 1 1 amb 0.5 0.5 0.5 emis 1 1 1 spec 0.5 0.5 0.5 shi 64 trans 0\n'
        non_empty = [o for o in self.objects if not o.is_empty()]
        # FIXME: this doesnt handle nested kids properly
        s += 'OBJECT world\nkids %i\n' % len(non_empty)
        s += string.join([str(o) for o in non_empty], '')
        return s

    def write(self, file_name):
        f = open(file_name, 'w')
        f.write(str(self))
        f.close()

    def plot(self):
        non_empty = [o for o in self.objects if not o.is_empty()]
        for o in non_empty:
            o.plot()

    def read(self, file_name):
        """read an ac3d file. TODO: groups, nested kids"""
#        def convertObject(tokens):
#            pass
        def convertLMaterial(tokens):
            self.material_list.append(tokens[1])

        def convertLObj(tokens):
            self.new_object(None, None)
            self._current_object._type = tokens[1]


        def convertLKids(tokens):
            self._current_object.kids = int(tokens[1])

        def convertLData(tokens):
            pass

        def convertLName(tokens):
            self._current_object.name = tokens[1].strip('"\'')

        def convertLTexture(tokens):
            texture = tokens[1].strip('"\'')
            self._current_object.texture = texture
            if texture not in self.texture_list:
                self.texture_list.append(texture)

        def _token2array(tokens, num):
            return np.array([float(item) for item in tokens[1:num + 1]])

        def convertLTexrep(tokens):
            self._current_object.texrep = _token2array(tokens, 2)

        def convertLTexoff(tokens):
            self._current_object.texoff = _token2array(tokens, 2)

        def convertLRot(tokens):
            self._current_object.rot = _token2array(tokens, 9)

        def convertLCrease(tokens):
            self._current_object.crease = tokens[1]

        def convertLLoc(tokens):
            self._current_object.loc = _token2array(tokens, 3)

        def convertLUrl(tokens):
            self._current_object.url = tokens[1]

        def convertLVertex(tokens):
            self._current_object.node(tokens[0], tokens[1], tokens[2])

        def convertSurf(tokens):
            assert(tokens[0] == 'SURF')
            assert(tokens[2] == 'mat')
            assert(tokens[4] == 'refs')
            self._current_object.face(nodes_uv_list = tokens[6], typ = tokens[1], mat = tokens[3])

        def convertIntegers(tokens):
            return int(tokens[0])

        def convertFloats(tokens):
            try:
                return float(tokens[0])
            except ValueError:
                logging.error(tokens[0])

        integer = Word( nums ).setParseAction( convertIntegers )
        string = Regex(r'"[^"]*"')
        floatNumber = Regex(r'[+-]?(\d+(\.\d*)?|(\.\d*))([eE][+-]\d+)?').setParseAction( convertFloats )
        anything = Regex(r'.*')

        debug = False

#       Relaxed see Tor_Ness_Lighthouse.xml
        lHeader = Regex('AC3Db[S]*') + LineEnd()
        lMaterial = (Literal('MATERIAL') + anything + LineEnd()).setParseAction(convertLMaterial).setDebug(debug)
        lObject = (Literal('OBJECT') + Word(alphas)).setParseAction(convertLObj).setDebug(debug)
        lKids = (Literal('kids') + integer).setParseAction(convertLKids).setDebug(debug)
        lName = (Literal('name') + string).setParseAction(convertLName).setDebug(debug)
        lData = (Literal('data') + integer + LineEnd() + anything + LineEnd()).setParseAction(convertLData).setDebug(debug)
        lTexture = (Literal('texture') + string ).setParseAction(convertLTexture).setDebug(debug)
        lTexrep = (Literal('texrep') + floatNumber + floatNumber ).setParseAction(convertLTexrep).setDebug(debug)
        lTexoff = (Literal('texoff') + floatNumber + floatNumber ).setParseAction(convertLTexoff).setDebug(debug)
        lRot = (Literal('rot') + floatNumber + floatNumber + floatNumber + floatNumber + floatNumber + floatNumber + floatNumber + floatNumber + floatNumber).setParseAction(convertLRot).setDebug(debug)
        lLoc = (Literal('loc') + floatNumber + floatNumber + floatNumber).setParseAction(convertLLoc)
        lCrease = (Literal('crease') + floatNumber).setParseAction(convertLCrease).setDebug(debug)
        lUrl = (Literal('url') + string).setParseAction(convertLUrl).setDebug(debug)
        lNumvert = Literal('numvert') + Word(nums)
        lVertex = (floatNumber + floatNumber + floatNumber).setParseAction(convertLVertex)
        lNumsurf = Literal('numsurf') + Word(nums)
        lSurf = Literal('SURF') + Word(alphanums)
        lMat = Literal('mat') + integer
        lRefs = Literal('refs') + integer
        lNodes = Group(integer + floatNumber + floatNumber)

        pObjectWorld = Group(lObject + Optional(lName) + lKids)
        pSurf = (lSurf + Optional(lMat) + lRefs + Group(OneOrMore(lNodes))).setParseAction( convertSurf )
        pObjectHeader = Group(lObject + Each([Optional(lName), Optional(lData), Optional(lTexture), Optional(lTexrep), \
            Optional(lTexoff), Optional(lRot), Optional(lLoc), Optional(lUrl), Optional(lCrease)]))
        pObject = Group(pObjectHeader + Optional(lNumvert + Group(ZeroOrMore(lVertex)) \
                   + Optional(lNumsurf + Group(ZeroOrMore(pSurf)))) \
          + lKids)#.setParseAction( convertObject )
#         pObject.setDebug(True)
#         pObject.debug = True
#         ParserElement.verbose_stacktrace = True

        pFile = lHeader + Group(OneOrMore(lMaterial)) + pObjectWorld \
          + Group(OneOrMore(pObject))

        try:
            self.p = pFile.parseFile(file_name)
        except IOError, e:
            logging.warning(e)

        # todo:
        # groups -- how do they work?


if __name__ == "__main__":
    a = File()
    #a.read('big-hangar.ac')
    #nn =  a.nodes_as_array()
    #print nn.shape
    #print "%s" % str(a)
    from math import sin, cos, radians
    if 0:
        a = File()
        a.new_object('bla', '')
        a.node(0,0,0)
        a.node(0,0,1)
        a.node(1,0,1)
        a.node(1,0,0)
        a.face([(0,0,0), (1,0,0), (2,0,0), (3,0,0)])
        print a.total_faces(), a.total_nodes()
        nodes = a.nodes_as_array()


        ac_nodes = np.array([[0, 0]])
        for x, y, z in nodes:
            node = np.dot(Rot_mat, [-z, -x]).reshape(1, 2)
            ac_nodes = np.append(ac_nodes, node, 0)

    angle = radians(98.9)
    Rot_mat = np.array([[cos(angle), -sin(angle)],
                        [sin(angle), cos(angle)]])

#     a = File("C:/Users/keith.paterson/Documents/FlightGear/TerraSync\Objects\e010n50\e012n51\EDDP_DHL_hangar.ac")
#     a = File("C:/Users/keith.paterson/Documents/FlightGear/TerraSync\Objects\e010n50\e012n51\eddp_antonov_hangar.ac")
    #a = File("C:/Users/keith.paterson/Documents/FlightGear/TerraSync/Objects/e010n50\e013n51/frauenkirche.ac")
    a = File("/mnt/hgfs/albrecht/daten/fgfs/fg_scenery/Scenery-TerraSync/Objects/e010n50/e012n51/eddp_antonov_hangar.ac")
    #a = File("/mnt/hgfs/albrecht/daten/fgfs/fg_scenery/Scenery-TerraSync/Objects/e010n50/e013n51/frauenkirche.ac") 
    #a = File("/mnt/hgfs/albrecht/daten/fgfs/fg_scenery/Scenery-TerraSync/Objects/e010n50/e012n51/EDDP_TerminalC.ac")
    #for o in a.objects:
    #    print "n", o.name, o.kids, o._type
    nodes = -np.delete(a.nodes_as_array().transpose(), 1, 0)[::-1]
    r = np.dot(Rot_mat, nodes)

    print a.total_faces()
    print a.total_nodes()


    if 1:
        #plt.clf()
        #a.plot()
        plt.xlim(-50,50)
        plt.ylim(-50,50)
# plt.show()

    plt.plot(nodes[0], nodes[1], 'k-')
    r = np.dot(Rot_mat, nodes)
    #plt.plot(r[0], r[1], 'r-')
    plt.show()
    print ac_nodes
    print nodes

    bla
    node = np.array([-float(splitted[2]),
                    - float(splitted[0])])

    node = np.dot(Rot_mat, node).reshape(1, 2)
    ac_nodes = np.append(ac_nodes, node, 0)

#        a.write('test.ac')
