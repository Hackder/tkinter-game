class EntityState:
    def update(self) -> list[str]:
        changed = []
        for name, value in vars(self).items():
            if name.startswith("_bound_"):
                new_value = value()
                field_name = name[7:]
                c = new_value != getattr(self, field_name)
                if c:
                    changed.append(field_name)
                setattr(self, field_name, value())

        return changed
