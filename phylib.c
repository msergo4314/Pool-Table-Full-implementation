#include "phylib.h"
// other preprocessor directives are in phylib.h

phylib_object *phylib_new_still_ball(unsigned char number, phylib_coord *pos) {
    if (pos == NULL) {
        // printf("Cannot create object with no position\n");
        return NULL; // return NULL(??)
    }
    phylib_object *my_still_ball = (phylib_object *)malloc(sizeof(phylib_object)); // malloc space
    // need to return if failed
    if (my_still_ball == NULL) {
        // printf("malloc failed\n");
        return NULL;
    }
    // printf("malloced space at %p (new still ball)\n", (void*)my_still_ball);
    my_still_ball->type = PHYLIB_STILL_BALL;
    my_still_ball->obj.still_ball.number = number; // set number
    my_still_ball->obj.still_ball.pos = *pos;
    // my_still_ball->obj.still_ball.pos.x = pos->x; // set position (we know pos is not NULL)
    // my_still_ball->obj.still_ball.pos.y = pos->y;
    return my_still_ball;
}

phylib_object *phylib_new_rolling_ball(unsigned char number, phylib_coord *pos, phylib_coord *vel, phylib_coord *acc) {
    if (pos == NULL || vel == NULL || acc == NULL) {
        // printf("Cannot create object with no position/velocity/acceleration\n");
        return NULL;
    }
    phylib_object *my_rolling_ball = (phylib_object *)malloc(sizeof(phylib_object)); // malloc space
    // need to return if failed
    if (my_rolling_ball == NULL) {
        // printf("malloc failed\n");
        return NULL;
    }
    // printf("malloced space at %p (new rolling ball)\n", (void*)my_rolling_ball);
    my_rolling_ball->type = PHYLIB_ROLLING_BALL;
    my_rolling_ball->obj.rolling_ball.number = number; // set number

    my_rolling_ball->obj.rolling_ball.pos.x = pos->x; 
    my_rolling_ball->obj.rolling_ball.pos.y = pos->y; 
    my_rolling_ball->obj.rolling_ball.vel.x = vel->x; // set velocity
    my_rolling_ball->obj.rolling_ball.vel.y = vel->y;
    my_rolling_ball->obj.rolling_ball.acc.x = acc->x; // set acceleration
    my_rolling_ball->obj.rolling_ball.acc.y = acc->y;
    return my_rolling_ball;
}

phylib_object *phylib_new_hole(phylib_coord *pos) {
    if (pos == NULL) {
        // printf("Cannot create hole with no position\n");
        return NULL;
    }
    phylib_object *my_hole = (phylib_object *)malloc(sizeof(phylib_object)); // malloc space
    // need to return if failed
    if (my_hole == NULL) {
        // printf("malloc failed\n");
        return NULL;
    }
    // printf("malloced space at %p (new hole)\n", (void*)my_hole);
    my_hole->type = PHYLIB_HOLE;
    (my_hole->obj).hole.pos.x = pos->x; // set x position
    (my_hole->obj).hole.pos.y = pos->y; // set y position
    return my_hole;
}

phylib_object *phylib_new_hcushion(double y) {
    phylib_object *my_hcushion = (phylib_object *)malloc(sizeof(phylib_object)); // malloc space
    // need to return if failed
    if (my_hcushion == NULL) {
        // printf("malloc failed\n");
        return NULL;
    }
    // printf("malloced space at %p (new hcushion)\n", (void*)my_hcushion);
    my_hcushion->type = PHYLIB_HCUSHION;
    my_hcushion->obj.hcushion.y = y;
    return my_hcushion;
}

phylib_object *phylib_new_vcushion(double x) {
    phylib_object *my_vcushion = (phylib_object *)malloc(sizeof(phylib_object)); // malloc space
    // need to return if failed
    if (my_vcushion == NULL) {
        // printf("malloc failed\n");
        return NULL;
    }
    // printf("malloced space at %p (new vcushion)\n", (void*)my_vcushion);
    my_vcushion->type = PHYLIB_VCUSHION;
    my_vcushion->obj.vcushion.x = x;
    return my_vcushion;
}

phylib_table *phylib_new_table(void) {
    phylib_table *table = (phylib_table*)malloc(sizeof(phylib_table));
    if (table == NULL) {
        // printf("could not allocate table properly");
        return NULL;
    }
    // printf("malloced space at %p (new phylib_table)\n", (void*)table);

    for (int i = 0; i < PHYLIB_MAX_OBJECTS; i++) {
        (table->object)[i] = NULL; // set all to NULL first, then overwrite
    }
    // need to add first 10 elements: 4 cusions, and 6 holes
    phylib_add_object(table, phylib_new_hcushion(0.0)); // first h cushion at 0
    phylib_add_object(table, phylib_new_hcushion(PHYLIB_TABLE_LENGTH)); // then another h cushion at max length
    
    phylib_add_object(table, phylib_new_vcushion(0.0)); // v cushion at 0
    phylib_add_object(table, phylib_new_vcushion(PHYLIB_TABLE_WIDTH)); // then another v cushion (also max length)

    // not sure if the order of these 6 holes actually matters...
    phylib_coord coord;
    coord.x = 0.0;
    coord.y = 0.0;
    phylib_add_object(table, phylib_new_hole(&coord));
    
    coord.x = 0.0;
    coord.y = PHYLIB_TABLE_LENGTH / 2;
    phylib_add_object(table, phylib_new_hole(&coord));
    
    coord.x = 0.0;
    coord.y = PHYLIB_TABLE_LENGTH;
    phylib_add_object(table, phylib_new_hole(&coord));
    
    coord.x = PHYLIB_TABLE_WIDTH;
    coord.y = 0.0;
    phylib_add_object(table,  phylib_new_hole(&coord));
    
    coord.x = PHYLIB_TABLE_WIDTH;
    coord.y = PHYLIB_TABLE_LENGTH / 2;
    phylib_add_object(table, phylib_new_hole(&coord));
    
    coord.x = PHYLIB_TABLE_WIDTH;
    coord.y = PHYLIB_TABLE_LENGTH;
    phylib_add_object(table, phylib_new_hole(&coord));
    table->time = 0.0; // initialize time to 0
    for (int i = 0; i < 10; i++) {
        if ((table->object)[i] == NULL) {
            printf("One of the first 10 elements was not allocated even though it should have been!\n");
        }
    }
    return table;
}

void phylib_copy_object(phylib_object **dest, phylib_object **src) {
    // printf("malloced space at %p for copied object\n", (void*)location);
    if (src == NULL || dest == NULL) {
        return;
    }
    if (*src == NULL) {
        // printf("*src is NULL\n");
        *dest = NULL; // set destination to source which is NULL
        return;
    }
    // even if *src == NULL, memcpy will work
    // printf("attempting to copy object type %d\n", (*src)->type);
    *dest = (phylib_object*)malloc(sizeof(phylib_object));
    if(*dest == NULL) {
        // printf("malloc failed\n");
        return;
    }
    memcpy(*dest, *src, sizeof(phylib_object));
    return;
}

phylib_table *phylib_copy_table(phylib_table *table) {
    if (table == NULL) {
        return NULL;
    }
    // use phylib_new_table since it also does the holes/cushions
    phylib_table *new_table = (phylib_table *)malloc(sizeof(phylib_table));
    if (new_table == NULL) {
        // printf("Error with malloc for copy table\n");
        return NULL;
    }
    // printf("malloced space at %p for copied table\n", (void*)new_table);
    for (int i = 0; i < PHYLIB_MAX_OBJECTS; i++) {
        phylib_copy_object(&(new_table->object[i]), &(table->object[i]));   
    }
    new_table->time = table->time;
    return new_table;
}

void phylib_add_object(phylib_table *table, phylib_object *object) {
    if (table == NULL) {
        // printf("The table is NULL\n");
        return;
    }
    if (object == NULL) {
        // printf("The object is NULL\n"); // would still work since object is not dereferenced but good to check
        return;
    }
    for (int i = 0; i < PHYLIB_MAX_OBJECTS; i++) {
        if ((table->object)[i] == NULL) {
           (table->object)[i] = object;
            return;
        }
    }
}

void phylib_free_table(phylib_table *table) {
    if (table == NULL) {
        // printf("the table is null and cannot be freed\n");
        return;
    }
    for (int i = 0; i < PHYLIB_MAX_OBJECTS; i++) {
        if ((table->object)[i] != NULL) {
            free((table->object)[i]);
            (table->object)[i] = NULL;
        }
    }
    free(table);
}

phylib_coord phylib_sub(phylib_coord c1, phylib_coord c2) {
    phylib_coord diff = {
    (c1.x - c2.x),
    (c1.y - c2.y)
    };
    return diff;
}

double phylib_length(phylib_coord c) {
    return sqrt(c.x * c.x + c.y * c.y);
}

double phylib_dot_product(phylib_coord b, phylib_coord a) {
    return a.x * b.x + a.y * b.y;
}

double phylib_distance(phylib_object *obj1, phylib_object *obj2) {
    if (obj1 == NULL || obj2 == NULL) {
        // printf("One or both of the objects are NULL\n");
        return -2.0;
    }
    if (obj1->type != PHYLIB_ROLLING_BALL) {
        // printf("Object one MUST be a rolling ball!\n");
        return -1.0;
    }
    switch(obj2->type) {
        case PHYLIB_ROLLING_BALL: // should be able to merge the first two cases but no need to risk it
            return phylib_length(phylib_sub((obj1->obj).rolling_ball.pos, (obj2->obj).rolling_ball.pos)) - PHYLIB_BALL_DIAMETER;
        case PHYLIB_STILL_BALL:
            return phylib_length(phylib_sub((obj1->obj).rolling_ball.pos, (obj2->obj).still_ball.pos))- PHYLIB_BALL_DIAMETER;
        case PHYLIB_HOLE:
            return phylib_length(phylib_sub((obj1->obj).rolling_ball.pos, (obj2->obj).hole.pos))- PHYLIB_HOLE_RADIUS;
        case PHYLIB_HCUSHION:
            return fabs(obj1->obj.rolling_ball.pos.y - obj2->obj.hcushion.y) - PHYLIB_BALL_RADIUS;
        case PHYLIB_VCUSHION:
            return fabs(obj1->obj.rolling_ball.pos.x - obj2->obj.vcushion.x) - PHYLIB_BALL_RADIUS;
        default:
            // return -1.0 if object two has an invalid type
            return -1.0;
    }
}

bool same_sign(double a, double b) {
    return ((a <= 0 && b <= 0) || (a >= 0 && b >=0));
}

void phylib_roll(phylib_object *new, phylib_object *old, double time) {
    if (new == NULL || old == NULL) {
        return; // do nothing if both are not rolling balls
    }
    if (new->type !=  PHYLIB_ROLLING_BALL|| old->type != PHYLIB_ROLLING_BALL) {
        return;
    }
    double position_old_x = old->obj.rolling_ball.pos.x;
    double position_old_y = old->obj.rolling_ball.pos.y;
    double velocity_old_x = old->obj.rolling_ball.vel.x;
    double velocity_old_y = old->obj.rolling_ball.vel.y;
    double acceleration_old_x = old->obj.rolling_ball.acc.x;
    double acceleration_old_y = old->obj.rolling_ball.acc.y;

    // set the new position
    new->obj.rolling_ball.pos.x = position_old_x + velocity_old_x * time + (0.5) * acceleration_old_x * time * time; // avoid pow
    new->obj.rolling_ball.pos.y = position_old_y + velocity_old_y * time + (0.5) * acceleration_old_y * time * time;
    // set new velocity
    new->obj.rolling_ball.vel.x = velocity_old_x + acceleration_old_x * time;
    new->obj.rolling_ball.vel.y = velocity_old_y + acceleration_old_y * time;
    // in the event of a sign change (on vel), set velocity and acceleration to be 0
    if (new->obj.rolling_ball.vel.x * velocity_old_x < 0) {
        new->obj.rolling_ball.vel.x = 0.0;
        new->obj.rolling_ball.acc.x = 0.0;
    }
    if (new->obj.rolling_ball.vel.y * velocity_old_y < 0) {
        new->obj.rolling_ball.vel.y = 0.0;
        new->obj.rolling_ball.acc.y = 0.0;
    }
    return;
}

unsigned char phylib_stopped(phylib_object *object) {
    if (object == NULL) {
        // printf("passed in NULL pointer\n");
        return 0; // not sure what to return here since nothing in document
        // in theory this will never be needed
    }
    if (object->type != PHYLIB_ROLLING_BALL) { // not actually necessary but whatever
        // printf("Unexpected object type. Expected rolling ball\n");
        return 0; // if not a rolling ball, then it's definitely stopped
    }
    // if velocity is < epsilon then it's stopped
    // printf("Velocity: %3.3f\n", phylib_length(object->obj.rolling_ball.vel));
    if (phylib_length(object->obj.rolling_ball.vel) < PHYLIB_VEL_EPSILON) { // length is always positive
        unsigned char number = object->obj.rolling_ball.number;
        double pos_x  = object->obj.rolling_ball.pos.x;
        double pos_y  = object->obj.rolling_ball.pos.y;
        // set the type to still, then make sure number and position is the same
        // printf("converted moving ball to still ball\n");
        object->type = PHYLIB_STILL_BALL;
        object->obj.still_ball.number = number;
        object->obj.still_ball.pos.x = pos_x;
        object->obj.still_ball.pos.y = pos_y;
        return 1; // converted to still ball
    }
    return 0; // default case
}

void phylib_bounce(phylib_object **a, phylib_object **b) {
    if (a == NULL || b == NULL) {
        printf("Cannot bounce NULL objects!\n");
        return;
    }
    phylib_object *a_ptr = (phylib_object *)(*a), *b_ptr = (phylib_object *)(*b);

    if (a_ptr == NULL || b_ptr == NULL) {
        return;
    }
    if (a_ptr->type != PHYLIB_ROLLING_BALL) {
        printf("The first object must be a rolling ball!\n");
        return;
    }
    switch(b_ptr->type) {
        case PHYLIB_HCUSHION:
            // velocity and acceleration are reversed for y
            a_ptr->obj.rolling_ball.vel.y *= -1;
            a_ptr->obj.rolling_ball.acc.y *= -1;
            break;
        case PHYLIB_VCUSHION:
            // velocity and acceleration are reversed for x
            a_ptr->obj.rolling_ball.vel.x *= -1;
            a_ptr->obj.rolling_ball.acc.x *= -1;
            break;
        case PHYLIB_HOLE:
            // free the memory of b, then set a to null;
            // printf("freeing ball %p since hole collision\n", (void*)*a);
            free(a_ptr);
            *a = NULL; // works because of double pointer otherwise this would be local
            break;
        case PHYLIB_STILL_BALL: ;
            unsigned char number = b_ptr->obj.still_ball.number;
            double pos_x = b_ptr->obj.still_ball.pos.x;
            double pos_y = b_ptr->obj.still_ball.pos.y;
            b_ptr->type = PHYLIB_ROLLING_BALL;
            b_ptr->obj.rolling_ball.number = number;
            // printf("still ball becomes moving ball\n");
            b_ptr->obj.rolling_ball.pos.x = pos_x;
            b_ptr->obj.rolling_ball.pos.y = pos_y;
            b_ptr->obj.rolling_ball.vel.x = 0.0;
            b_ptr->obj.rolling_ball.vel.y = 0.0;
            b_ptr->obj.rolling_ball.acc.x = 0.0;
            b_ptr->obj.rolling_ball.acc.y = 0.0;
            // go to case 5 (rolling ball, since still ball is now a rolling ball)
        case PHYLIB_ROLLING_BALL: ;
            // printf("Two rolling balls collide\n");
            // difference between a and b for position and velocity (a - b)
            phylib_coord r_ab = phylib_sub(a_ptr->obj.rolling_ball.pos, b_ptr->obj.rolling_ball.pos);

            // relative velocity of a with respect to b
            phylib_coord v_rel = phylib_sub(a_ptr->obj.rolling_ball.vel, b_ptr->obj.rolling_ball.vel);

            phylib_coord n; // make a unit vector n
            n.x = 0.0; // these should get replaced
            n.y = 0.0;
            // better hope phylib length doesn't return 0 here
            if (phylib_length(r_ab) != 0.0) {
                n.x = r_ab.x / phylib_length(r_ab);
                n.y = r_ab.y / phylib_length(r_ab);
            }
            // v_rel is relative velocity in the direction of a
            double v_rel_n = phylib_dot_product(n, v_rel);
            // velocity of ball a is decreased by v_rel_n * n.(x || y)
            a_ptr->obj.rolling_ball.vel.x -= (v_rel_n * n.x);
            a_ptr->obj.rolling_ball.vel.y -= (v_rel_n * n.y);

            // velocity of ball b is given by initial plus v_rel_n * n(x || y)
            b_ptr->obj.rolling_ball.vel.x += (v_rel_n * n.x);
            b_ptr->obj.rolling_ball.vel.y += (v_rel_n * n.y);
            
            double speed_a = phylib_length(a_ptr->obj.rolling_ball.vel);
            if (speed_a > PHYLIB_VEL_EPSILON) {
                // set acceleration to negative velocity divided by speed multiplied by drag
                a_ptr->obj.rolling_ball.acc.x = (-a_ptr->obj.rolling_ball.vel.x * (PHYLIB_DRAG)) / speed_a;
                a_ptr->obj.rolling_ball.acc.y = (-a_ptr->obj.rolling_ball.vel.y * (PHYLIB_DRAG)) / speed_a;
            }
            double speed_b = phylib_length(b_ptr->obj.rolling_ball.vel);
            if (speed_b > PHYLIB_VEL_EPSILON) {
                // set acceleration to negative velocity divided by speed multiplied by drag
                b_ptr->obj.rolling_ball.acc.x = (-b_ptr->obj.rolling_ball.vel.x * (PHYLIB_DRAG)) / speed_b;
                b_ptr->obj.rolling_ball.acc.y = (-b_ptr->obj.rolling_ball.vel.y * (PHYLIB_DRAG)) / speed_b;
            }
            break;
        default: ;
            // printf("Default case.\n");
    }
}

unsigned char phylib_rolling(phylib_table *t) {
    unsigned char count = 0;
    if (t == NULL) {
        // printf("Table is NULL!\n");
        return 0;
    }
    for (int i = 0; i < PHYLIB_MAX_OBJECTS; i++) {
        if ((t->object)[i] != NULL) {
            if (((t->object)[i])->type == PHYLIB_ROLLING_BALL) {
                count++;
            }
        }
    }
    return count;
}

phylib_table *phylib_segment(phylib_table *table) {
    if (table == NULL) {
        // printf("table is NULL\n");
        return NULL;
    }
    if (phylib_rolling(table) == 0) {
        // if no rollling balls return NULL
        return NULL;
    }
    double time = PHYLIB_SIM_RATE;
    phylib_table *new_table = phylib_copy_table(table);
    if (new_table != NULL) {
        while (time < PHYLIB_MAX_TIME) {
            for (int i = 0; i < PHYLIB_MAX_OBJECTS; i++) {
                if (new_table->object[i] != NULL && (new_table->object)[i]->type == PHYLIB_ROLLING_BALL) {
                    phylib_roll((new_table->object)[i], (table->object)[i], time);
                }
            }
            for (int i = 0; i < PHYLIB_MAX_OBJECTS; i++) {
                if (new_table->object[i] && new_table->object[i]->type == PHYLIB_ROLLING_BALL) {
                    for(int j = 0; j < PHYLIB_MAX_OBJECTS; j++) {
                        if ((new_table->object)[i] != NULL && (new_table->object)[j] != NULL && j != i && (new_table->object)[i]->type == PHYLIB_ROLLING_BALL) {
                            if (phylib_distance((new_table->object)[i], (new_table->object)[j]) < 0.0) {
                                phylib_bounce(&((new_table->object)[i]), &((new_table->object)[j]));
                                goto function_exit;
                            }
                        }
                    }
                    if (phylib_stopped((new_table->object)[i])) {
                        goto function_exit;
                    }
                }
            }
        time += PHYLIB_SIM_RATE;
        }
    function_exit:
    new_table->time += time;
    return new_table;
    }
    return NULL;
}

char *phylib_object_string(phylib_object *object) {
    static char string[80];
    if (object == NULL)
    {
        sprintf(string, "NULL;");
        return string;
    }
    switch (object->type)
    {
    case PHYLIB_STILL_BALL:
        sprintf(string,
                "STILL_BALL (%d,%6.1lf,%6.1lf)",
                object->obj.still_ball.number,
                object->obj.still_ball.pos.x,
                object->obj.still_ball.pos.y);
        break;
    case PHYLIB_ROLLING_BALL:
        sprintf(string,
                "ROLLING_BALL (%d,%6.1lf,%6.1lf,%6.1lf,%6.1lf,%6.1lf,%6.1lf)",
                object->obj.rolling_ball.number,
                object->obj.rolling_ball.pos.x,
                object->obj.rolling_ball.pos.y,
                object->obj.rolling_ball.vel.x,
                object->obj.rolling_ball.vel.y,
                object->obj.rolling_ball.acc.x,
                object->obj.rolling_ball.acc.y);
        break;
    case PHYLIB_HOLE:
        sprintf(string,
                "HOLE (%6.1lf,%6.1lf)",
                object->obj.hole.pos.x,
                object->obj.hole.pos.y);
        break;
    case PHYLIB_HCUSHION:
        sprintf(string,
                "HCUSHION (%6.1lf)",
                object->obj.hcushion.y);
        break;
    case PHYLIB_VCUSHION:
        sprintf(string,
                "VCUSHION (%6.1lf)",
                object->obj.vcushion.x);
        break;
    }
    return string;
}
