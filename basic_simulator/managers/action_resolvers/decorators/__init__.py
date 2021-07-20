import random
import numpy as np
from decopatch import function_decorator, WRAPPED, F_ARGS, F_KWARGS

from data_models.actions import ActionStatus
from data_models.entities.status_effects import Dead, Unconscious
from utility.coordinates import cubic_manhattan


@function_decorator
def require_consciousness(fn=WRAPPED, f_args=F_ARGS, f_kwargs=F_KWARGS):
    self, action = f_kwargs['self'], f_kwargs['action']
    actor_model = self.simulation_manager.being_model_manager.get(action.actor)

    if actor_model.status_effects.is_affected_by(Dead) or actor_model.status_effects.is_affected_by(
            Unconscious):
        action.status = ActionStatus.FAILED
        action.reason = "Actor is required to be alive and conscious"
        return

    return fn(*f_args, **f_kwargs)


@function_decorator
def require_proximity(exact=None, at_least=None, at_most=None, fn=WRAPPED, f_args=F_ARGS, f_kwargs=F_KWARGS):
    self, action = f_kwargs['self'], f_kwargs['action']
    sub_loc = self.simulation_manager.grid_model.get_location(action.actor)

    if action.target_id is None:
        action.status = ActionStatus.FAILED
        action.reason = "No entity is targeted for proximity"
        return
    else:
        tar_loc = self.simulation_manager.grid_model.get_location(action.target_id)
        dist = cubic_manhattan(sub_loc, tar_loc)

        if exact is not None and dist != exact:
            action.status = ActionStatus.FAILED
            action.reason = "Target proximity was not exactly equal to %d, value: %d" % (exact, dist)
            return

        if at_least is not None and dist <= at_least:
            action.status = ActionStatus.FAILED
            action.reason = "Target proximity was not at least equal to %d, value: %d" % (at_least, dist)
            return

        if at_most is not None and dist >= at_most:
            action.status = ActionStatus.FAILED
            action.reason = "Target proximity was not at most equal to %d, value: %d" % (at_most, dist)
            return

        return fn(*f_args, **f_kwargs)


@function_decorator
def require_target_type(target_type: type = None, fn=WRAPPED, f_args=F_ARGS, f_kwargs=F_KWARGS):
    self, action = f_kwargs['self'], f_kwargs['action']

    if action.target_id is None:
        action.status = ActionStatus.FAILED
        action.reason = "No target specified when determining type"
        return
    else:
        target_model = self.simulation_manager.simulation_manager.get(action.target_id)
        if not isinstance(target_model, target_type):
            action.status = ActionStatus.FAILED
            action.reason = "Target was not of the required type of %s, value: %s" % (target_type, type(target_model))
            return

        return fn(*f_args, **f_kwargs)


@function_decorator
def required_target(ignore_self=True, explicit=True, selection_type: type = None, fn=WRAPPED, f_args=F_ARGS, f_kwargs=F_KWARGS):
    self, action = f_kwargs['self'], f_kwargs['action']

    # If there is already a target, evaluate the action.
    if action.target_id is not None:
        # Verify the target exists
        if action.target_id not in self.simulation_manager.entity_model_manager:
            action.status = ActionStatus.FAILED
            action.reason = "Specified target does not exist"
            return

        return fn(*f_args, **f_kwargs)

    # If no random selection should be made, then not specifying a target could be ambiguous.
    if explicit:
        action.status = ActionStatus.FAILED
        action.reason = "No explicit target was specified, ambiguity is disallowed"
        return

    # Otherwise, select from the different types of targeting, resolving ambiguity by random selection.
    actor_loc = self.simulation_manager.grid_model.get_location(action.actor)
    if hasattr(action, 'direction') and action.direction is not None:
        dst_loc = np.add(action.direction.value, actor_loc)
        dst_entities_by_id = self.simulation_manager.grid_model.at(dst_loc).entities
    elif hasattr(action, 'location') and action.location is not None:
        dst_entities_by_id = self.simulation_manager.grid_model.at(action.location).entities
    else:
        dst_entities_by_id = self.simulation_manager.grid_model.at(actor_loc).entities

    # Remove the actor from the possible selections.
    if ignore_self and action.actor in dst_entities_by_id:
        dst_entities_by_id.remove(action.actor)

    # If no choices left, the action cant be resolved.
    if len(dst_entities_by_id) == 0:
        action.status = ActionStatus.FAILED
        action.reason = "No entities left to randomly select from"
        return
    else:
        # If there is a stipulation of selection type, pull down the data data_models to verify their type.
        if selection_type is not None:
            dst_entities = map(lambda e_id: self.simulation_manager.entity_model_manager[e_id], dst_entities_by_id)
            # Filter only data_models with the selection type.
            dst_entities_by_id = list(
                map(lambda e: e.entity_id,
                    filter(lambda e: isinstance(e, selection_type), dst_entities)
                    )
            )
        action.target_id = random.choice(dst_entities_by_id)

    return fn(*f_args, **f_kwargs)


@function_decorator
def required_terrain(ignore_self=True, selection_type: type = None, fn=WRAPPED, f_args=F_ARGS, f_kwargs=F_KWARGS):
    self, action = f_kwargs['self'], f_kwargs['action']

    # Select from the different types of targeting, resolving ambiguity by random selection.
    actor_loc = self.simulation_manager.grid_model.get_location(action.actor)
    if hasattr(action, 'direction') and action.direction is not None:
        dst_loc = np.add(action.direction.value, actor_loc)
        dst_terrain = self.simulation_manager.grid_model.at(dst_loc).terrain
    elif hasattr(action, 'location') and action.location is not None:
        dst_terrain = self.simulation_manager.grid_model.at(action.location).terrain
    else:
        dst_terrain = self.simulation_manager.grid_model.at(actor_loc).terrain

    # If no choices left, the action cant be resolved.
    if len(dst_terrain) == 0:
        action.status = ActionStatus.FAILED
        action.reason = "No terrain left to randomly select from"
        return
    else:
        # If there is a stipulation of selection type, pull down the data data_models to verify their type.
        if selection_type is not None:
            # Filter only data_models with the selection type.
            dst_terrain = list(filter(lambda e: isinstance(e, selection_type), dst_terrain))

        if len(dst_terrain) == 0:
            action.status = ActionStatus.FAILED
            action.reason = "No terrain left to randomly select from"
            return

        action.target = random.choice(dst_terrain)

    return fn(*f_args, **f_kwargs)
