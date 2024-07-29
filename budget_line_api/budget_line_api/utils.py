
def get_and_delete_last_uuid(model):
    try:
        # Récupérer le dernier enregistrement par date de création (tri par ordre décroissant)
        dernier_objet = model.objects.latest('time_created')

        # Récupérer l'UUID de l'objet à supprimer
        dernier_uuid = dernier_objet.id

        # Supprimer l'objet
        dernier_objet.delete()

        print(f"Dernier enregistrement avec UUID {dernier_uuid} supprimé avec succès.")

    except model.DoesNotExist:
        print("Aucun enregistrement trouvé dans la base de données.")