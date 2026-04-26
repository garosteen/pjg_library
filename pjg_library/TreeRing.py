import random
import numpy as np
from noise import *
from shapely import affinity
from shapely.geometry import LinearRing,LineString, Point,Polygon, GeometryCollection, MultiLineString
import os, sys
from pjg_library import SketchBorder
from pjg_library import utilityfunctions as uf
from pjg_library import boilerplate
from shapely.validation import make_valid,explain_validity
from shapely.ops import unary_union
from shapely import line_merge
import math

class TreeRing:
    def __init__(self,center=(0,0),species=None):
        self.center = center
        self.rings = []
        self.poly_rings = []
        if species is None:
            self.randomize_species()
        else:
            self.clone(species)

        self.noisex = random.random()*1000
        self.noisey = random.random()*1000
        self.year = random.randrange(2000)
        self.current_year = self.year
        self.outer_bound = None

    def print_info(self):
        print(self.year)
        print("-- NOISE RADIUS INFO --")
        print(f" base: {self.noise_radius_base}")
        print(f" inc: {self.noise_radius_increment}")
        print(f" drift: {self.noise_radius_drift}")
        print(f"Max Width: {self.max_width}")
        print(f"Early Wood Ratio: {self.early_wood_ratio}")
        print(f" -- NOISE INFO --")
        print(f"  oct: {self.noise_octaves}")
        print(f"  str: {self.noise_warp_strength}")
        print(f"  sze: {self.noise_warp_size}")

    def randomize_species(self):
        self.noise_radius_base = random.random()*0.5 # 0.5 is pretty wobbly, 0 is a circle
        self.noise_radius_increment = random.random()*0.04 # 0.02 is good. 0.05 is VERY wobbly, 0.005 is VERY not.
        self.noise_radius_drift = np.random.normal(loc=0.0,scale=0.2) # Focus closer to 0, because otherwise it doesn't matter much
        self.noise_octaves = 3+random.randrange(5) # Even 2 octaves sometimes looks really bland
        self.noise_warp_strength = random.random()*2.0
        self.noise_warp_size = random.random()*0.4
        self.max_width = random.random()*0.75 + 0.25 # Don't want it too small, but also not too big. 
        self.peak_year = random.randrange(20) # 7
        self.growth_change = 2 + random.randrange(30)
        self.early_wood_ratio = random.random()*0.5 + 0.45 
        self.late_wood_ratio = 1.0 - self.early_wood_ratio
        # CRACKS
        self.crack_freq = random.random()*4.0+0.25
        self.crack_close_chance = random.random()+0.5
        self.crack_close_speed = random.random()*0.5
        self.crack_close_trigger_width = 1.0 + random.random()*3.0 
        self.crack_close_balance_min = random.random()*0.5 # Min growth balance value to ignore 
        self.crack_shift_eccentricity = random.random()*0.2

    def clone(self,species):
        #self.noisex = species.noisex 
        #self.noisey = species.noisey 
        self.noise_radius_base = species.noise_radius_base 
        self.noise_radius_increment = species.noise_radius_increment 
        self.noise_radius_drift = species.noise_radius_drift 
        self.noise_octaves = species.noise_octaves 
        self.noise_warp_strength = species.noise_warp_strength 
        self.noise_warp_size = species.noise_warp_size 
        self.max_width = species.max_width 
        self.peak_year = species.peak_year 
        self.growth_change = species.growth_change 
        self.early_wood_ratio = species.early_wood_ratio 
        self.late_wood_ratio = species.late_wood_ratio 
        # CRACKS# 
        self.crack_freq = species.crack_freq 
        self.crack_close_chance = species.crack_close_chance 
        self.crack_close_speed = species.crack_close_speed 
        self.crack_close_trigger_width = species.crack_close_trigger_width 
        self.crack_close_balance_min = species.crack_close_balance_min 
        self.crack_shift_eccentricity = species.crack_shift_eccentricity 

    def translate(self, xoff, yoff):
        self.center = (self.center[0] + xoff, self.center[1] + yoff)
        print(self.rings)
        for i in range(len(self.rings)):
            self.rings[i] = affinity.translate(self.rings[i], xoff=xoff, yoff=yoff)
        print(self.poly_rings)
        for i in range(len(self.poly_rings)):
            self.poly_rings[i] = affinity.translate(self.poly_rings[i], xoff=xoff, yoff=yoff)

    def get_radius(self,index,theta):
        """Get the distance from center for a given ring index and angle"""
        if index<0:
            # TODO: this seems like nonsense
            # TODO: Figure out how to get this to return 0 without errors
            #print("Why is the code asking for sub-zero indices?")
            return 0.1

        if len(self.rings) <= index:
            print("Asked for radius of ring that doesn't exist")
            index = len(self.rings)-1

        # Create a line from origin to some large distance at angle theta
        # TODO: is it possible for this to fail, if the tree ring is too big?
        testline = LineString([self.center,uf.getxy(self.center[0],self.center[1],100,theta)])

        # Calculate intersection with that line and the ring at that index
        p = testline.intersection(self.rings[index])
        # TODO: SOMETIMES p is a LineString??
        if (p.geom_type == "LineString"):
            p = Point(p.coords[0])
        end = np.array([p.x, p.y])
        start = np.asarray(self.center)
        d = np.linalg.norm(start-end) # They say this is the fastest distance function
        return d

    def get_outer_radius(self):
        """Convenience function to get outermost radius at angle 0"""
        return self.get_radius(len(self.rings)-1,0)

    def get_noise_val(self,index,theta):
        base_r = self.noise_radius_base 
        r_factor = self.noise_radius_increment 
        i_factor = self.noise_radius_drift 
        r = base_r + index*r_factor
        x = self.noisex + index*i_factor
        y = self.noisey + index*i_factor
        p = uf.getxy(x,y,r,theta)
        warpstrength = self.noise_warp_strength
        warpsize = self.noise_warp_size
        o = self.noise_octaves 
        val = snoise3(p[0],p[1],warpstrength*snoise2(p[0]*warpsize,p[1]*warpsize),octaves=o) 
        val = (1+val)/2.0
        
        return val

    def generate_ring(self,index):
        """Generate the ring at the index, and all previous rings if not generated."""
        if len(self.rings) < index:
            self.generate_ring(index-1)

        ring = []
        base_radius = self.get_radius(index-1,0) # Just for calculating how many segments we need to do
        arc = 0.05
        if index == 0:
            arc = arc/2.0
        steps = 2*np.pi*base_radius/arc
        fixed_growth = 0.0 # 0.02
        year = index // 2 # Every two rings is a year
        growth_factor = self.get_yearly_growth(year)
        centerx = self.center[0]
        centery = self.center[1]

        if index%2 == 1:
            fixed_growth = 0.0
            growth_factor = growth_factor*self.late_wood_ratio # 0.1
        else:
            growth_factor = growth_factor*self.early_wood_ratio

        for t in np.linspace(0,2*np.pi,int(steps)):
            r = self.get_radius(index-1,t)
            noise = self.get_noise_val(index,t)
            r = r + fixed_growth + growth_factor*noise
            point = uf.getxy(centerx,centery,r,t)
            ring.append(point)

        self.rings.append(LinearRing(ring))

    def grow(self,years=1):
        """Add this many years to the growth"""

        for y in range(years):
            early_ring = []
            late_ring = []
            base_radius = self.get_outer_radius() # to calculate number of segments
            index = len(self.rings)

            arc = 0.05 # 0.05

            if len(self.rings) < 2:
                # Higher resolution for the innermost rings
                arc = arc/2.0

            steps = 2*np.pi*base_radius/arc
            year = self.current_year 
            centerx = self.center[0]
            centery = self.center[1]
            growth_factor = self.get_yearly_growth(y)
            early_growth_factor = growth_factor*self.early_wood_ratio
            late_growth_factor = growth_factor * self.late_wood_ratio

            for t in np.linspace(0,2*np.pi,int(steps)):
                er = self.get_radius(index-1,t)
                enoise = self.get_noise_val(index,t)
                er = er + early_growth_factor*enoise
                epoint = uf.getxy(centerx,centery,er,t)
                early_ring.append(epoint)

                lr = er
                lnoise = self.get_noise_val(index+1,t)
                lr = lr + late_growth_factor*lnoise
                lpoint = uf.getxy(centerx,centery,lr,t)
                late_ring.append(lpoint)

                # TODO: This would be a good place to calculate the average width of each ring, for future data.
                # Subtract original er from lr, get the width, make an array of all the widths, average it, store average width of every ring.

            self.rings.append(LinearRing(early_ring))
            self.rings.append(LinearRing(late_ring))
            self.outer_bound = Polygon(late_ring)
            self.current_year = self.current_year+1

            if index == 0:
                filled_ring = Polygon(self.rings[index])
            else:
                filled_ring = Polygon(self.rings[index],holes=[self.rings[index-1]])
            self.poly_rings.append(filled_ring)

    def get_yearly_growth(self,t):
        climate = self.max_width*(snoise2(self.year+t,1)+0.5)
        min_growth = 0.1
        #print(f"Climate for {self.year+t} is {climate}")
        growth = self.max_width * np.exp(-1*((t-self.peak_year)**2)/(self.growth_change*self.growth_change))+climate
        if growth < min_growth:
            growth = min_growth
        return growth

    def generate_cracks(self):
        # TODO: Larger cracks should be rarer, or the tree should have some sort of individual distribution of crack sizes

        self.cracks = []
        #crack_freq = 2.0 # One crack per ring
        num_cracks = int(self.crack_freq * len(self.poly_rings))
        # print(f"Chance: {self.crack_close_chance}, speed:{self.crack_close_speed}\nwidth:{self.crack_close_trigger_width}")

        for c in range(num_cracks):
            crack = [] # For accumulating points in the crack object
            crack_start_width = 0.05
            crack_width = crack_start_width 

            crack_center_angle = random.random()*2*np.pi 
            crack_start_angle = crack_center_angle 
            crack_end_angle = crack_center_angle
            crack_growth_balance = random.random() # 0.5 is evenly balanced, >0.5 tends to shrink, <0.5 tends to grow
            crack_growth_factor = random.random() * 0.1 # 0.1 Maximum change in size
            centerx = self.center[0]
            centery = self.center[1]
            # Starting ring is more likely to be toward the outer rings because they have more area
            # Formula based on areas of rings increasing by factors of odd numbers
            start_ring = 2*math.ceil(math.sqrt(random.randrange(((len(self.rings)-1)//2)**2)))
            center_radius = self.get_radius(start_ring,crack_center_angle)

            for ring in range(len(self.rings)):
                if ring < start_ring:
                    continue
                if ring%2 == 1:
                    # Odd ring: do angle offsets and width adjustments
                    max_shift = crack_width*self.crack_shift_eccentricity # Bigger cracks can shift more -- is this what I want?
                    max_shift_angle = max_shift / center_radius 
                    shift = np.random.normal(loc=0,scale=max_shift_angle)
                    crack_center_angle += shift
                    center_radius = self.get_radius(ring,crack_center_angle)
                    crack_width += (random.random()-crack_growth_balance)*crack_growth_factor
                    crack_end_angle = crack_center_angle + (crack_width/2.0) / center_radius 
                    crack_start_angle = crack_center_angle - (crack_width/2.0) / center_radius 
                
                if crack_width <= 0:
                    break

                start_radius = self.get_radius(ring,crack_start_angle)
                startxy = uf.getxy(centerx,centery,start_radius,crack_start_angle)

                end_radius = self.get_radius(ring,crack_end_angle)
                endxy = uf.getxy(centerx,centery,end_radius,crack_end_angle)

                crack.append(startxy)
                crack.insert(0,endxy) # Is constantly inserting at 0 going to be problematic?
                if (    crack_growth_balance > self.crack_close_balance_min 
                        and crack_width >= self.crack_close_trigger_width*crack_start_width 
                        and random.random() <= self.crack_close_chance):
                    # If not a "fast growing" crack, and bigger than 2x starting size, encourage it to close
                    crack_growth_balance = crack_growth_balance+self.crack_close_speed # Slightly increase, to encourage closing the crack
            
            if crack_width >= 0 and len(crack) > 2:
                # crack meets the outer edge, must follow edge to accomodate that
                arc = 0.05
                steps = (crack_end_angle-crack_start_angle)*center_radius/arc
                outer_ring = len(self.rings) - 1 
                for t in np.linspace(crack_start_angle,crack_end_angle,int(steps)):
                    r = self.get_radius(outer_ring,t)
                    xy = uf.getxy(centerx,centery,r,t)
                    crack.append(xy)

            if len(crack) > 2:
                polycrack = Polygon(crack)
                self.cracks.append(make_valid(polycrack))

    def crack(self):
        self.generate_cracks()
        for i in range(len(self.poly_rings)):
            for c in self.cracks:
                self.poly_rings[i] = make_valid(self.poly_rings[i]).difference(c)
